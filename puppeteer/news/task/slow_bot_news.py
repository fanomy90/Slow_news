import os
from pathlib import Path
import sys
import logging

# Получаем путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Добавляем корневую директорию в PYTHONPATH
sys.path.append(project_root)
# Укажите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puppeteer.settings')
import django
django.setup()

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("/var/log/bot.log"),
                        # logging.StreamHandler()
                        logging.StreamHandler(sys.stdout),  # вывод логов в stdout
    ]
)

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

#получить подписчиков на новости
# def get_subscribers_to_news(subscribers, category, message_format):
#     return subscribers.filter(subscribed_to_categories=category, message_format=message_format)

#сборка сообщения перед отправкой
def prepare_and_send_news(subscribers, article, category_style, content, image, message_format):
    from news.slow_bot import send_message_with_retry
    for subscriber in subscribers:
        message = (
            f'{category_style} <b>{article.cat.name} {article.date}</b>\n\n'
            f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n'
            f'{content}\n'
            f'{trim_author(article.author)}'
        )
        print(f"Отправка {message_format} категории {article.cat.name} новостного сообщения пользователю {subscriber.chat_id}")
        logging.info(f"Отправка {message_format} категории {article.cat.name} новостного сообщения пользователю {subscriber.chat_id}")
        # Получаем функцию для рассылки через отложенный импорт
        success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
        if success:
            print(f"Новостное сообщение {message_format} категории {article.cat.name} успешно отправлено пользователю {subscriber.chat_id}")
            logging.info(f"Новостное сообщение {message_format} категории {article.cat.name} успешно отправлено пользователю {subscriber.chat_id}")
        else:
            print(f"Ошибка при отправке {message_format} категории {article.cat.name} новостного сообщения пользователю {subscriber.chat_id}")
            logging.error(f"Ошибка при отправке {message_format} категории {article.cat.name} новостного сообщения пользователю {subscriber.chat_id}")
        # if not success:
        #     logging.error(f"Ошибка при отправке {message_format} сообщения пользователю {subscriber.chat_id}")


# def send_news(type_message="news", frequency_sending="every_hour"):
def send_news_frequency(frequency_sending="every_hour"):
    #получаем подписчиков по частатое рассылки через отложенный импорт
    from news.models import TelegramSubscriber, News, Category
    subscribers = TelegramSubscriber.objects.filter(frequency_sending=frequency_sending)

    if subscribers.exists():
        #стилизация категории новости
        categories = Category.objects.all()
        category_styles = {
            'Безопасность': '🔒',
            'Статьи': '📄',
            'Обзоры': '🔍',
            'Интервью': '🗣️',
        }
        #прокоходим по категориям новостей
        for category in categories:
            cat_news_subscribers = subscribers.filter(subscribed_to_categories=category)
            if cat_news_subscribers.exists():
                #получаем новости категории
                news = News.objects.filter(cat=category, is_published=True, is_sent=False)
                if news.exists():
                    for article in news:
                        category_style = category_styles.get(category.name, 'i')
                        image = article.image if article.image else None
                        # Подписчики для коротких новостей по категории
                        #short_news_subscribers = get_subscribers_to_news(subscribers, category, "short")
                        short_cat_news_subscribers = cat_news_subscribers.filter(message_format="short")
                        if short_cat_news_subscribers.exists():
                            short_content = (trim_content(article.content, word_limit=35) + '...')
                            #Подготовим и отправим сокращенные сообщения новостей по категориям
                            prepare_and_send_news(short_cat_news_subscribers, article, category_style, short_content, image, "short")
                            
                        else:
                            print(f"С периодичностью {frequency_sending} в категории {category.name} нет подписчиков на короткие сообщения")
                            logging.info(f"С периодичностью {frequency_sending} в категории {category.name} нет подписчиков на короткие сообщения")

                        # Подписчики для полных новостей по категории
                        #full_news_subscribers = get_subscribers_to_news(subscribers, category, "full")
                        full_cat_news_subscribers = cat_news_subscribers.filter(message_format="full")

                        if full_cat_news_subscribers.exists():
                            full_content = article.content
                            #Подготовим и отправим сокращенные сообщения новостей по категориям
                            prepare_and_send_news(full_cat_news_subscribers, article, category_style, full_content, image, "full")
                        else:
                            print(f"С периодичностью {frequency_sending} в категории {category.name} нет подписчиков на длинные сообщения")
                            logging.info(f"С периодичностью {frequency_sending} в категории {category.name} нет подписчиков на длинные сообщения")
                        # Отмечаем новость как отправленную
                        try:
                            article.is_sent = True
                            article.save()
                            print(f"Новость {article.title} помечена как отправленная.")
                            logging.info(f"Новость {article.title} помечена как отправленная.")
                        except Exception as e:
                            print(f"Ошибка при сохранении новости {article.title}: {str(e)}")
                            logging.error(f"Ошибка при сохранении новости {article.title}: {str(e)}")

                        # article.is_sent = True
                        # article.save()
                        # logging.info(f"Новость {article.title} помечена как отправленная.")
                else:
                    print(f"В категории {category.name} нет новостей для отправки.")
                    logging.info(f"В категории {category.name} нет новостей для отправки.")
            else:
                print(f"На рассылку новостей с периодичностью {frequency_sending} в категории {category.name} нет подписчиков")
                logging.info(f"На рассылку новостей с периодичностью {frequency_sending} в категории {category.name} нет подписчиков")
    else:
        print(f"На рассылку новостей с периодичностью {frequency_sending} нет подписчиков")
        logging.info(f"На рассылку новостей с периодичностью {frequency_sending} нет подписчиков")