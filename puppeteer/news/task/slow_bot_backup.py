import os
from pathlib import Path
import telebot
from telebot import types, TeleBot
import requests
import datetime
import sys

import logging
# from news.templatetags.news_tags import trim_author
from django.utils.html import linebreaks
from django.template.defaultfilters import truncatewords

# Получаем путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Добавляем корневую директорию в PYTHONPATH
sys.path.append(project_root)
# Укажите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puppeteer.settings')
import django
django.setup()
bot = TeleBot('5659259939:AAG5XXvMKpVzHC7YqZ2INM8wJ7ryu4gVdZU')
# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("/var/log/bot.log"),
                        # logging.StreamHandler()
                        logging.StreamHandler(sys.stdout),  # вывод логов в stdout
    ]
)

def trim_author(text):
    if text:
        # Ищем индекс первого вхождения двух пробелов
        index = text.find('  ')
        if index != -1:
            return text[:index]
    return text

def trim_content(content, word_limit=35):
    if not content:
        return ""  # Возвращаем пустую строку, если контент пустой
    # Обрезаем до 35 слов
    # Разбиваем текст на слова и обрезаем до word_limit
    words = content.split()[:word_limit]
    return ' '.join(words)  # Объединяем слова обратно в строку

@bot.message_handler(commands=['start'])
def start_message(message):
    print("Команда /start получена")  # Отладочная информация
    print(sys.path)
    logging.info("Команда /start получена")
    keyboard_category = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_category.add(types.KeyboardButton(text='Подписаться на рассылку'))
    keyboard_category.add(types.KeyboardButton(text='Отписаться от рассылки'))
    bot.send_message(
        message.chat.id,
        text=f"Добро пожаловать, {message.from_user.first_name}!\nВыберите действие:",
        reply_markup=keyboard_category
    )

@bot.message_handler(content_types=["text"])
def next_message(message):
    print(f"Получено сообщение: {message.text}")  # Логирование входящих сообщений
    print(sys.path)
    logging.info(f"Получено сообщение: {message.text}")
    if message.text.lower() == 'подписаться на рассылку' or message.text.lower() == '/subscribe':
        from news.models import TelegramSubscriber  # Отложенный импорт здесь
        chat_id = message.chat.id
        username = message.from_user.username

        subscriber, created = TelegramSubscriber.objects.get_or_create(
            chat_id=chat_id,
            defaults={'username': username}
        )
        
        if created:
            bot.send_message(chat_id, "Вы успешно подписались на рассылку новостей.")
        else:
            bot.send_message(chat_id, "Вы уже подписаны на рассылку.")
    
    elif message.text.lower() == 'отписаться от рассылки' or message.text.lower() == '/unsubscribe':
        print(sys.path)
        from news.models import TelegramSubscriber  # Отложенный импорт здесь
        chat_id = message.chat.id
        
        deleted, _ = TelegramSubscriber.objects.filter(chat_id=chat_id).delete()
        
        if deleted:
            bot.send_message(chat_id, "Вы успешно отписались от рассылки новостей.")
        else:
            bot.send_message(chat_id, "Вы не были подписаны.")
    
    else:
        bot.send_message(message.chat.id, f"Недоступная операция: {message.text}")
        logging.info(f"Недоступная операция: {message.text}")

def send_message_with_retry(subscriber, message, image=None, retries=3, delay=3):
    for attempt in range(retries):
        try:
            if image:
                logging.info(f"Отправка сообщения с картинкой пользователю {subscriber.chat_id}, попытка {attempt + 1}")
                bot.send_photo(chat_id=subscriber.chat_id, photo=image, caption=message, parse_mode="HTML")
            else:
                logging.info(f"Отправка простого сообщения без картинки пользователю {subscriber.chat_id}, попытка {attempt + 1}")
                bot.send_message(subscriber.chat_id, message, parse_mode="HTML")
            return True
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}, попытка {attempt + 1}")
            if attempt + 1 < retries:
                time.sleep(delay)
            else:
                return False
                

def send_news(type_message="news", frequency_sending="every_hour"):
    from news.models import TelegramSubscriber, News, Category  # Отложенный импорт здесь, добавить модель городов для прогноза и модель валют
    today = datetime.date.today()
    subscribers = TelegramSubscriber.objects.filter(frequency_sending=frequency_sending)

    if type_message == "news":
        print(f"Выполняется подготовка сообщения новостной рассылки")
        logging.info(f"Выполняется подготовка сообщения новостной рассылки")
        categories = Category.objects.all()
        
        for category in categories:
            print(f"Получаем новости по категориям")
            logging.info(f"Получаем новости по категориям")
            news = News.objects.filter(cat=category, is_published=True, is_sent=False)

            if news.exists():
                for article in news:
                    if not article.is_sent:
                        print(f"Формируем сообщение")
                        logging.info(f"Формируем сообщение")
                        category_styles = {
                            'Безопасность': '🔒',
                            'Статьи': '📄',
                            'Обзоры': '🔍',
                            'Интервью': '🗣️',
                        }
                        category_style = category_styles.get(category.name, 'i')
                        author = trim_author(article.author)

                        #переделать чтобы формировалось два типа сообщений и отправлялись пользователям
                        # if message_format == 'full':
                        #     content = article.content
                        # else:
                        #     content = trim_content(article.content, world_limit=35)

                        image = article.image if article.image else None

                        # Отправляем сообщение только тем пользователям, кто подписан на короткие типы новостей по категориям
                        subscribers_to_short_news = subscribers.filter(subscribed_to_categories=category, message_format="short")
                        for subscriber in subscribers_to_short_news:
                            content = trim_content(article.content, world_limit=35)
                            message = f'{category_style} <b>{category.name} {article.date}</b>\n\n' \
                                    f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n' \
                                    f'{content}\n' \
                                    f'{author}'
                            
                            print(f"Отправка короткого новостного сообщения пользователю {subscriber.chat_id}")
                            logging.info(f"Отправка короткого новостного сообщения пользователю {subscriber.chat_id}")
                            success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
                            if not success:
                                print(f"Ошибка при отправке короткого сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                                logging.info(f"Ошибка при отправке короткого сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
                        # Отправляем сообщение только тем пользователям, кто подписан на полные типы новостей по категориям
                        subscribers_to_full_news = subscribers.filter(subscribed_to_categories=category, message_format="full")
                        for subscriber in subscribers_to_full_news:
                            content = article.content
                            message = f'{category_style} <b>{category.name} {article.date}</b>\n\n' \
                                    f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n' \
                                    f'{content}\n' \
                                    f'{author}'
                            
                            print(f"Отправка длинного новостного сообщения пользователю {subscriber.chat_id}")
                            logging.info(f"Отправка длинного новостного сообщения пользователю {subscriber.chat_id}")
                            success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
                            if not success:
                                print(f"Ошибка при отправке длинного сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                                logging.info(f"Ошибка при отправке длинного сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")

                        # Помечаем новость как отправленную
                        print(f"Новость {article.title} помечена как отправленная.")
                        logging.info(f"Новость {article.title} помечена как отправленная.")
                        article.is_sent = True
                        article.save()

            else:
                print(f"В категории {category.name} нет новостей для отправки.")
                logging.info(f"В категории {category.name} нет новостей для отправки.")

    elif type_message == "weather":
        
        subscribers_to_short_weather = subscribers.filter(message_format="short")
        for subscriber in subscribers_to_short_weather:
            try:
                # Заглушка для погоды
                print(f"Отправка краткого прогноза погоды пользователю {subscriber.chat_id}")
                logging.info(f"Отправка краткого прогноза погоды пользователю {subscriber.chat_id}")
                image = None
                temp = "Температура"
                message = f'Краткий прогноз погоды для города\n' \
                        f'{temp}'
                success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
                if not success:
                    print(f"Ошибка при отправке краткого прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                    logging.info(f"Ошибка при отправке краткого прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
            except Exception as e:
                print(f"Ошибка при отправке краткого прогноза пользователю {subscriber.chat_id}: {e}")
                logging.info(f"Ошибка при отправке краткого прогноза пользователю {subscriber.chat_id}: {e}")

        subscribers_to_full_weather = subscribers.filter(message_format="full")
        for subscriber in subscribers_to_full_weather:
            try:
                # Заглушка для погоды
                print(f"Отправка полного прогноза погоды пользователю {subscriber.chat_id}")
                logging.info(f"Отправка полного прогноза погоды пользователю {subscriber.chat_id}")
                image = None
                temp = "Температура"
                message = f'Полный прогноз погоды для города\n' \
                        f'{temp}'
                success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
                if not success:
                    print(f"Ошибка при отправке полного прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                    logging.info(f"Ошибка при полного краткого прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
            except Exception as e:
                print(f"Ошибка при отправке полного прогноза пользователю {subscriber.chat_id}: {e}")
                logging.info(f"Ошибка при отправке полного прогноза пользователю {subscriber.chat_id}: {e}")

    elif type_message == "currency":
        for subscriber in subscribers:
            try:
                # Заглушка для курса валют
                image = None
                currency = "Список валют"
                message = f'Курс валют на \n' \
                        f'{currency}'
                success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
                if not success:
                    print(f"Ошибка при отправке курса валют пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                    logging.info(f"Ошибка при отправке курса валют пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
                print(f"Отправка курсов валют пользователю {subscriber.chat_id}")
                logging.info(f"Отправка курсов валют пользователю {subscriber.chat_id}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}")
                logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}")



    # # news = News.objects.filter(date=today, is_published=True, is_sent=False)
    # news = News.objects.filter(is_published=True, is_sent=False)
    # print(f"Найдено новостей для отправки: {news.count()}")
    # logging.info(f"Найдено новостей для отправки: {news.count()}")
    # #функция отправки сообщений с повторной отправкой в случае ошибок


    # def send_message_with_retry(subscriber, message, image=None, retries=3, delay=3):
    #     for attempt in range(retries):
    #         try:
    #             if image:
    #                 print(f"Отправка сообщения c картинкой пользователю {subscriber.chat_id}, попытка {attempt + 1}")
    #                 logging.info(f"Отправка сообщения c картинкой пользователю {subscriber.chat_id}, попытка {attempt + 1}")
    #                 bot.send_photo(chat_id=subscriber.chat_id, photo=image, caption=message, parse_mode="HTML")
    #             else:
    #                 print(f"Отправка простого сообщения без картинки пользователю {subscriber.chat_id}, попытка {attempt + 1}")
    #                 logging.info(f"Отправка простого сообщения без картинки пользователю {subscriber.chat_id}, попытка {attempt + 1}")
    #                 bot.send_message(subscriber.chat_id, message, parse_mode="HTML")
    #             return True  # Сообщение успешно отправлено, выход из цикла
    #         except Exception as e:
    #             print(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}, попытка {attempt + 1}")
    #             logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}, попытка {attempt + 1}")
    #             if attempt + 1 < retries:  # Если не последняя попытка, делаем паузу перед следующей
    #                 print(f"Задержка {delay} секунд перед повторной попыткой...")
    #                 time.sleep(delay)  # Задержка в несколько секунд
    #             else:
    #                 return False  # Если достигли лимита попыток
    # # если есть новости которые можно отправить то формируем сообщение
    # if news.exists():
    #     for article in news:
    #         if not article.is_sent:
    #             # добавляем стилизацию категории новости
    #             category = article.cat.name  # Извлекаем название категории
    #             category_styles = {
    #                 'Безопасность': '🔒',
    #                 'Статьи': '📄',
    #                 'Обзоры': '🔍',
    #                 'Интервью': '🗣️',
    #             }
    #             # делаем обрезание полей в сообщении
    #             author = trim_author(article.author)
    #             content = trim_content(article.content, word_limit=35)
    #             category_style = category_styles.get(category, 'ℹ️')  # Используем нейтральный символ
    #             print(f"Отправляем новость: {article.title}")
    #             logging.info(f"Отправляем новость: {article.title}")
    #             # собираем сообщение
    #             message = f'{category_style} <b>{category} {article.date}</b>\n\n' \
    #                     f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n' \
    #                     f'{content}\n' \
    #                     f'{author}'
    #                     # f'{article.author}'

    #             #цикл отправки сообщений по пользователям с переотправлением в случае ошибок
    #             for subscriber in subscribers:
    #                 image = article.image if article.image else None
    #                 success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
    #                 if not success:
    #                     print(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
    #                     logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
    #             #после отправки сообщений помечаем новость как отправленную
    #             article.is_sent = True
    #             print(f"Новость {article.title} помечена как отправленная.")
    #             logging.info(f"Новость {article.title} помечена как отправленная.")
    #             article.save()
    # else:
    #     for subscriber in subscribers:
    #         try:
    #             # bot.send_message(subscriber.chat_id, "На данный момент свежих новостей нет.")
    #             print(f"Отправка сообщения пользователю {subscriber.chat_id}: Новых сообщений нет")
    #             logging.info(f"Отправка сообщения пользователю {subscriber.chat_id}: Новых сообщений нет")
    #         except Exception as e:
    #             print(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}")
    #             logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}")

def run_bot():
    print("Запуск Telegram-бота...")
    logging.info("Запуск Telegram-бота...")
    # bot.polling(none_stop=True)
    try:
        #bot.polling(none_stop=True)
        # Запуск polling с настройкой тайм-аутов
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    run_bot()


# убрал чтобы запуск шел через Supervisor.
# if __name__ == "__main__":
#     try:
#         run_bot()
#     except Exception as e:
#         print(f"Ошибка при запуске бота: {e}")