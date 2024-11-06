import os
from pathlib import Path
import sys
import logging
import datetime
from django.db import transaction
from django.utils import timezone
# Получаем путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Добавляем корневую директорию в PYTHONPATH
sys.path.append(project_root)
# Укажите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puppeteer.settings')
import django

django.setup()
now = datetime.datetime.now()
#ограничение на максимальную длинну сообщения
MAX_MESSAGE_LENGTH = 4096
#обрезка автора
def trim_author(text):
    if text:
        # Ищем индекс первого вхождения двух пробелов
        index = text.find('  ')
        if index != -1:
            return text[:index]
    return text
#обрезка текста новости
def trim_content(content, word_limit=35):
    if not content:
        return ""  # Возвращаем пустую строку, если контент пустой
    # Обрезаем до 35 слов
    # Разбиваем текст на слова и обрезаем до word_limit
    words = content.split()[:word_limit]
    return ' '.join(words)  # Объединяем слова обратно в строку
#функция для разбивки сообщения на несколько для обхода лимита телеграмм
def split_message(full_content, max_length=MAX_MESSAGE_LENGTH):
    while full_content:
        split_at = full_content[:max_length].rfind(' ')
        if split_at == -1:
            split_at = max_length
        yield full_content[:split_at]
        full_content = full_content[split_at:].strip()

#сборка сообщения перед отправкой
def prepare_and_send_news(subscribers, article, category_style, content, image, message_format, is_first_message=True):
    from news.slow_bot import send_message_with_retry
    for subscriber in subscribers:
        # Формируем сообщение в зависимости от типа сообщения
        if message_format == "short":
            message = (
                f'{category_style} <b>{article.cat.name} {article.date}</b>\n\n'
                f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n'
                f'{content}\n'
                f'{trim_author(article.author)}'
            )
            print(f"{now} Отправка короткого сообщения категории {article.cat.name} пользователю {subscriber.username}")
        elif is_first_message:
            message = (
                f'{category_style} <b>{article.cat.name} {article.date}</b>\n\n'
                f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n'
                f'{trim_author(article.author)}'
            )
            print(f"{now} Отправка первой части полного сообщения категории {article.cat.name} пользователю {subscriber.username}")
        else:
            message = content
            print(f"{now} Отправка текстовой части полного сообщения категории {article.cat.name} пользователю {subscriber.username}")
        # Отправляем сообщение
        success = send_message_with_retry(subscriber, message, image if is_first_message else None, retries=3, delay=3)
        if success:
            print(f"{now} Сообщение категории {article.cat.name} успешно отправлено пользователю {subscriber.username}")
        else:
            print(f"{now} Ошибка при отправке сообщения категории {article.cat.name} пользователю {subscriber.username}")

def send_news_frequency(frequency_sending="every_hour"):
    from news.models import TelegramSubscriber, News, Category, NewsSent
    now = timezone.now()
    # Получаем всех подписчиков с указанной частотой рассылки
    subscribers = TelegramSubscriber.objects.filter(frequency_sending=frequency_sending)
    if not subscribers.exists():
        print(f"{now} На рассылку новостей с периодичностью {frequency_sending} нет подписчиков")
        return
    # Стилизация категории новостей - убрать в prepare_and_send_news
    category_styles = {
        'Безопасность': '🔒',
        'Статьи': '📄',
        'Обзоры': '🔍',
        'Интервью': '🗣️',
    }
    # Разделяем подписчиков по формату сообщений (короткие или полные)
    short_news_subscribers = subscribers.filter(message_format="short")
    full_news_subscribers = subscribers.filter(message_format="full")
    # Получаем все категории
    categories = Category.objects.all()
    # Прокручиваем категории и обрабатываем новости
    for category in categories:
        # Получаем новости, которые ещё не отправлены
        news_articles = News.objects.filter(
            cat=category, 
            is_published=True, 
            is_sent=False).exclude(
                newssent__subscriber__in=subscribers
            )
        if not news_articles.exists():
            print(f"{now} В категории {category.name} нет новостей для отправки.")
            continue
        category_style = category_styles.get(category.name, 'i')
        # Отправляем короткие новости
        if short_news_subscribers.exists():
            for article in news_articles:
                short_content = trim_content(article.content, word_limit=35) + '...'
                image = article.image if article.image else None
                prepare_and_send_news(short_news_subscribers, article, category_style, short_content, image, "short")
        else:
            print(f"{now} С периодичностью {frequency_sending} в категории {category.name} нет подписчиков на короткие сообщения")
        # Отправляем полные новости
        if full_news_subscribers.exists():
            for article in news_articles:
                full_content = article.content
                image = article.image if article.image else None
                # Отправляем первое сообщение с метаданными и картинкой
                prepare_and_send_news(full_news_subscribers, article, category_style, '', image, "full", is_first_message=True)
                # Разбиваем текст на части, если он превышает лимит
                for part in split_message(full_content):
                    prepare_and_send_news(full_news_subscribers, article, category_style, part, None, "full", is_first_message=False)
        else:
            print(f"{now} С периодичностью {frequency_sending} в категории {category.name} нет подписчиков на длинные сообщения")
        # Отмечаем новости как отправленные
        for article in news_articles:
            try:
                # article.is_sent = True
                # article.save()
                # print(f"{now} Новость {article.title} помечена как отправленная.")
                #добавляем метку отправки новости конкретному пользователю
                for subscriber in subscribers:
                    NewsSent.objects.create(subscriber=subscriber, news=article, sent_at=now)
                if not remaining_subscribers.exists():
                    article.is_sent = True
                    article.save()
                    print(f"{now} Новость {article.title} помечена как отправленная для пользователя {subscriber.username} в {now}.")
            except Exception as e:
                print(f"{now} Ошибка при сохранении новости {article.title}: {str(e)}")