import os
from pathlib import Path
import telebot
from telebot import types, TeleBot
import sys
import time
import logging
#проверить и убрать
from django.utils.html import linebreaks
from django.template.defaultfilters import truncatewords
import datetime
import requests
now = datetime.datetime.now()
# Получаем путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Добавляем корневую директорию в PYTHONPATH
sys.path.append(project_root)
# Укажите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puppeteer.settings')
import django
django.setup()
bot = TeleBot('5659259939:AAG5XXvMKpVzHC7YqZ2INM8wJ7ryu4gVdZU')
#убрать после перехода на расширенную подписку
def trim_author(text):
    if text:
        # Ищем индекс первого вхождения двух пробелов
        index = text.find('  ')
        if index != -1:
            return text[:index]
    return text
#убрать после перехода на расширенную подписку
def trim_content(content, word_limit=35):
    if not content:
        return ""  # Возвращаем пустую строку, если контент пустой
    # Обрезаем до 35 слов
    # Разбиваем текст на слова и обрезаем до word_limit
    words = content.split()[:word_limit]
    return ' '.join(words)  # Объединяем слова обратно в строку
#меню кнопок настроек рассылки
def settings_menu(call, message_header, subscriber):
    print(f"{now} Нажата кнопка {call.data} для настройки {message_header.lower()}")
    # Создаем клавиатуру
    keyboard_category = types.InlineKeyboardMarkup(row_width=1)
    # Проверяем состояние подписок и добавляем кнопки
    if not subscriber.news_sent:
        keyboard_category.add(types.InlineKeyboardButton('Включить рассылку новостей', callback_data='news_sent_on'))
    else:
        keyboard_category.add(types.InlineKeyboardButton('Отключить рассылку новостей', callback_data='news_sent_off'))
    if not subscriber.currency_sent:
        keyboard_category.add(types.InlineKeyboardButton('Включить рассылку курса валют', callback_data='currency_sent_on'))
    else:
        keyboard_category.add(types.InlineKeyboardButton('Отключить рассылку курса валют', callback_data='currency_sent_off'))
    if not subscriber.weather_sent:
        keyboard_category.add(types.InlineKeyboardButton('Включить рассылку прогноза погоды', callback_data='weather_sent_on'))
    else:
        keyboard_category.add(types.InlineKeyboardButton('Отключить рассылку прогноза погоды', callback_data='weather_sent_off'))
    # Настройки формата сообщений
    if subscriber.message_format == 'short':
        keyboard_category.add(types.InlineKeyboardButton('Полные сообщения', callback_data='full'))
    else:
        keyboard_category.add(types.InlineKeyboardButton('Сокращенные сообщения', callback_data='short'))
    # Настройки частоты рассылки
    if subscriber.frequency_sending != 'every_hour':
        keyboard_category.add(types.InlineKeyboardButton('Каждый час', callback_data='every_hour'))
    if subscriber.frequency_sending != 'every_3hour':
        keyboard_category.add(types.InlineKeyboardButton('Каждые 3 часа', callback_data='every_3hour'))
    if subscriber.frequency_sending != 'every_6hour':
        keyboard_category.add(types.InlineKeyboardButton('Каждые 6 часов', callback_data='every_6hour'))
    if subscriber.frequency_sending != 'every_9hour':
        keyboard_category.add(types.InlineKeyboardButton('Каждые 9 часов', callback_data='every_9hour'))
    if subscriber.frequency_sending != 'every_12hour':
        keyboard_category.add(types.InlineKeyboardButton('Каждые 12 часов', callback_data='every_12hour'))
    if subscriber.frequency_sending != 'daily':
        keyboard_category.add(types.InlineKeyboardButton('Ежедневно', callback_data='daily'))
    # Кнопка для возврата
    keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
    # Формируем текст сообщения
    subscribed_categories = subscriber.subscribed_to_categories.all()
    subscribed_category_names = [category.name for category in subscribed_categories]
    message_text = (
        f'{message_header}\n\n'
        f'Текущие настройки:\n'
        f'Рассылка новостей: {"включена" if subscriber.news_sent else "отключена"}\n'
        f'Рассылка курса валюты: {"включена" if subscriber.currency_sent else "отключена"}\n'
        f'Рассылка погоды: {"включена" if subscriber.weather_sent else "отключена"}\n'
        f'Периодичность рассылки: {subscriber.get_frequency_sending_display()}\n'
        f'Тип сообщений: {subscriber.get_message_format_display()}\n'
        f'Категории новостей: {", ".join(subscribed_category_names) if subscribed_category_names else "не выбраны"}'
    )
    # Обновляем сообщение
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
#меню кнопок подписки
def subscribe_menu(call, message_header, subscriber, categories):
    print(f"{now} Нажата кнопка {call.data} для настройки {message_header.lower()}")
    keyboard_category = types.InlineKeyboardMarkup(row_width=1)
    if subscriber:
        print(f"{now} Получен пользователь для подписки: {subscriber.username}")
        subscribed_categories = subscriber.subscribed_to_categories.all()
        print(f"{now} Получены категории новостей пользователя {subscriber.username} для подписки: {subscribed_categories}")
        def send_message_text(call, message_header, message_botom):
            message_text = (
                f'{message_header}\n\n'
                f'{message_botom}\n'
            )
            bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
        # Фильтруем категории, исключая уже подписанные
        for category in categories:
            if category not in subscribed_categories:
                keyboard_category.add(types.InlineKeyboardButton(category.name, callback_data=f'newsSubscribe_{category.id}'))
        if not keyboard_category.keyboard:
            keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))  # Если нет доступных категорий
            send_message_text(call, message_header, 'Нет доступных категорий для подписки.')
            #bot.edit_message_text('Нет доступных категорий для подписки.', call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
        else:
            keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
            send_message_text(call, message_header, 'Выберите категории для подписки')
            #bot.edit_message_text('Выберите категории для подписки', call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
    else:
        print(f"{now} Пользователя {call.message.chat.id} еще нет в базе подписчиков")
        # Добавляем все категории, так как пользователь новый
        for category in categories:
            keyboard_category.add(types.InlineKeyboardButton(category.name, callback_data=f'newsSubscribe_{category.id}'))
        keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
        bot.edit_message_text(message_header, call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)

def unsubscribe_menu(call, message_header, subscriber, categories):
    print(f"{now} Нажата кнопка {call.data} для настройки {message_header.lower()}")
    def send_message_text(call, message_header, message_botom):
        message_text = (
            f'{message_header}\n\n'
            f'{message_botom}\n'
        )
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
    keyboard_category = types.InlineKeyboardMarkup(row_width=1)
    if categories.exists():
        print(f"{now} Получены категории пользователя {subscriber.username} для отписки: {categories}")
        for category in categories:
            keyboard_category.add(types.InlineKeyboardButton(category.name, callback_data=f'newsUnsubscribe_{category.id}'))
        keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
        send_message_text(call, message_header, 'Выберите категории для отписки.')
        #bot.edit_message_text('Выберите категории для отписки', call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
    else:
        print(f"{now} У пользователя {subscriber.username} нет подписок")
        keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
        send_message_text(call, message_header, f'У пользователя {subscriber.username} нет подписок')
        #bot.edit_message_text(f'У пользователя {subscriber.username} нет подписок', call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)

#функция для вывода меню городов для подписки на прогноз погоды
def subscribe_weather_menu(call, message_header, subscriber, cities):
    print(f"{now} Нажата кнопка {call.data} для настройки {message_header.lower()}")
    # Создаем клавиатуру
    keyboard_city = types.InlineKeyboardMarkup(row_width=1)
    if subscriber:
        print(f"{now} Получен пользователь для подписки прогноза погоды: {subscriber.username}")
        subscribed_cities = subscriber.subscribed_weather_city.all()
        print(f"{now} Получены города {subscribed_cities} на прогноз погоды которых подписан пользователя {subscriber.username}")
        def send_message_text(call, message_header, message_botom):
            message_text = (
                f'{message_header}\n\n'
                f'{message_botom}\n'
            )
            bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard_city)
        for city in cities:
            if city not in subscribed_cities:
                keyboard_city.add(types.InlineKeyboardButton(city.city_name, callback_data=f'citySubscribe_{city.id}'))
        if not keyboard_city.keyboard:
            keyboard_city.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
            send_message_text(call, message_header, 'Нет доступных городов для подписки на прогноз погоды.')
        else:
            keyboard_city.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
            send_message_text(call, message_header, 'Выберите город для подписки на прогноз погоды')
    else:
        print(f"{now} Пользователя {call.message.chat.id} еще нет в базе подписчиков")
        for city in cities:
            keyboard_city.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
            send_message_text(call, message_header, 'Новый пользователь. Выберите город для подписки на прогноз погоды')
            bot.edit_message_text(message_header, call.message.chat.id, call.message.message_id, reply_markup=keyboard_city)
#функия вывода городов для отписки от прогноза погоды
def unsubscribe_weather_menu(call, message_header, subscriber, cities):
    print(f"{now} Нажата кнопка {call.data} для настройки {message_header.lower()}")
    def send_message_text(call, message_header, message_botom):
        message_text = (
            f'{message_header}\n\n'
            f'{message_botom}\n'
        )
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard_city)
    keyboard_city = types.InlineKeyboardMarkup(row_width=1)
    # if cities.exists():
    if cities:
        print(f"{now} Получены города {cities} пользователя {subscriber.username} для отписки от прогноза погоды")
        for city in cities:
            keyboard_city.add(types.InlineKeyboardButton(city.city_name, callback_data=f'cityUnsubscribe_{city.id}'))
        keyboard_city.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
        send_message_text(call, message_header, 'Выберите город для отписки.')
    else:
        print(f"{now} У пользователя {subscriber.username} нет доступных городов для отписки от прогноза погоды")
        keyboard_city.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
        send_message_text(call, message_header, f'У пользователя {subscriber.username} нет городов для отписки от прогноза погоды')

#функция отправки сообщений с повторной отправкой в случае ошибок
def send_message_with_retry(subscriber, message, image=None, retries=3, delay=3):
    for attempt in range(retries):
        try:
            if image:
                print(f"{now} Отправка сообщения c картинкой пользователю {subscriber.username}, попытка {attempt + 1}")
                #logging.info(f"Отправка сообщения c картинкой пользователю {subscriber.username}, попытка {attempt + 1}")
                bot.send_photo(chat_id=subscriber.chat_id, photo=image, caption=message, parse_mode="HTML")
            else:
                print(f"{now} Отправка простого сообщения без картинки пользователю {subscriber.username}, попытка {attempt + 1}")
                #logging.info(f"Отправка простого сообщения без картинки пользователю {subscriber.username}, попытка {attempt + 1}")
                bot.send_message(subscriber.chat_id, message, parse_mode="HTML")
            return True  # Сообщение успешно отправлено, выход из цикла
        except Exception as e:
            print(f"{now} Ошибка при отправке сообщения пользователю {subscriber.username}: {e}, попытка {attempt + 1}")
            #logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.username}: {e}, попытка {attempt + 1}")
            if attempt + 1 < retries:  # Если не последняя попытка, делаем паузу перед следующей
                #print(f"Задержка {delay} секунд перед повторной попыткой...")
                time.sleep(delay)  # Задержка в несколько секунд
            else:
                return False  # Если достигли лимита попыток

@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"{now} Команда /start получена")  # Отладочная информация
    keyboard_category = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_category.add(types.KeyboardButton(text='Подписаться на рассылку'))
    keyboard_category.add(types.KeyboardButton(text='Отписаться от рассылки'))
    keyboard_category.add(types.KeyboardButton(text='Управление подпиской'))
    bot.send_message(
        message.chat.id,
        text=f"Добро пожаловать, {message.from_user.first_name}!\nВыберите действие:",
        reply_markup=keyboard_category
    )

@bot.message_handler(content_types=["text"])
def next_message(message):
    print(f"{now} Получено сообщение: {message.text}")  # Логирование входящих сообщений
    #print(sys.path)
    #logging.info(f"Получено сообщение: {message.text}")
    from news.models import TelegramSubscriber
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
        from news.models import TelegramSubscriber  # Отложенный импорт здесь
        chat_id = message.chat.id
        deleted, _ = TelegramSubscriber.objects.filter(chat_id=chat_id).delete()        
        if deleted:
            bot.send_message(chat_id, "Вы успешно отписались от рассылки новостей.")
        else:
            bot.send_message(chat_id, "Вы не были подписаны.")
    #меню подписки на новости
    elif message.text.lower() == 'управление подпиской' or message.text.lower() == '/settings':
        keyboard_subcategory = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('Подписаться на категории новостей', callback_data='key1')
        button2 = types.InlineKeyboardButton('Отписаться от категории новостей', callback_data='key2')
        button3 = types.InlineKeyboardButton('Подписаться на прогноз погоды', callback_data='key3')
        button4 = types.InlineKeyboardButton('Отписаться от прогноза погоды', callback_data='key4')
        button5 = types.InlineKeyboardButton('Подписаться на курсы валют', callback_data='key5')
        button6 = types.InlineKeyboardButton('Отписаться от курсов валют', callback_data='key6')
        button7 = types.InlineKeyboardButton('Настройка рассылки', callback_data='key7')
        keyboard_subcategory.add(button1, button2, button3, button4, button5, button6, button7)
        bot.send_message(message.chat.id, text='Выберите операцию', reply_markup=keyboard_subcategory)
    else:
        bot.send_message(message.chat.id, f"Недоступная операция: {message.text}")
        logging.info(f"Недоступная операция: {message.text}")
        
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    from news.models import TelegramSubscriber, Category, Currency, City
    if call.data == 'key0':
        keyboard_category = types.InlineKeyboardMarkup(row_width=1)
        keyboard_category.add(types.InlineKeyboardButton('Подписаться на категории новостей', callback_data='key1'),
                        types.InlineKeyboardButton('Отписаться от категории новостей', callback_data='key2'),
                        types.InlineKeyboardButton('Подписаться на прогноз погоды', callback_data='key3'),
                        types.InlineKeyboardButton('Отписаться от прогноза погоды', callback_data='key4'),
                        types.InlineKeyboardButton('Подписаться на курсы валют', callback_data='key5'),
                        types.InlineKeyboardButton('Отписаться от курсов валют', callback_data='key6'),
                        types.InlineKeyboardButton('Настройка рассылки', callback_data='key7'))
        bot.edit_message_text('Выберите операцию', call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
    #ветка подписки на категории новостей
    elif call.data == 'key1':
        subscriber = TelegramSubscriber.objects.filter(chat_id=call.message.chat.id).first()
        categories = Category.objects.all()
        print(f"{now} Получены категории для подписки: {categories}")
        subscribe_menu(call, 'Вы находитесь в разделе выбора подписки на категорию новостей.', subscriber, categories)
    # Обработка выбора категории для подписки
    elif call.data.startswith('newsSubscribe_'):
        category_id = call.data.split('_')[1]  # Получаем ID категории из callback_data
        print(f"{now} Нажата кнопка id={category_id} для добавления подписки")
        #from news.models import TelegramSubscriber, Category
        categories = Category.objects.all()
        category = categories.filter(id=category_id).first()
        #category = Category.objects.get(id=category_id)
        print(f"{now} Получена категория {category} для подписки пользователя")
        # Получаем username пользователя, если он существует
        username = call.message.chat.username if call.message.chat.username else "Неизвестный пользователь"
        # Ищем или создаем подписчика по его chat_id
        subscriber, created = TelegramSubscriber.objects.get_or_create(chat_id=call.message.chat.id, defaults={'username': username})
        print(f"{now} Получен пользователь {subscriber.username} для добавления подписки")
        # Добавляем категорию в подписку
        subscriber.subscribed_to_categories.add(category)
        subscriber.news_sent = True  # Устанавливаем подписку на новости
        subscriber.save()
        print(f"{now} Добавлена категория {category} подписки пользователя {subscriber.username}")
        subscribe_menu(call, f"Добавлена категория {category}", subscriber, categories)
    elif call.data == 'key2':
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        categories = subscriber.subscribed_to_categories.all()
        unsubscribe_menu(call, 'Вы находитесь в разделе выбора категории для отписки от новостей.', subscriber, categories)
    # Обработка выбора категории для отписки
    elif call.data.startswith('newsUnsubscribe_'):
        category_id = call.data.split('_')[1]  # Получаем ID категории из callback_data
        print(f"{now} Нажата кнопка id={category_id} для удаления подписки")
        category = Category.objects.filter(id=category_id).first()
        print(f"{now} Получена категория {category} для удаления из подписки пользователя")
        # Ищем подписчика по его chat_id
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для удаления из подписки")
        # Убираем категорию из подписки
        subscriber.subscribed_to_categories.remove(category)
        if not subscriber.subscribed_to_categories.exists():
            subscriber.news_sent = False  # Отписка от новостей
        subscriber.save()
        print(f"{now} Удаление категории {category} из подписки пользователя {subscriber.username}")
        categories = subscriber.subscribed_to_categories.all()
        unsubscribe_menu(call, f'Вы отписались от категории: {category.name}', subscriber, categories)
    #добавить ветку погоды
    # Обработка ветки подписки на прогноз погоды
    elif call.data == 'key3':
        subscriber = TelegramSubscriber.objects.filter(chat_id=call.message.chat.id).first()
        cities = City.objects.all()
        subscribe_weather_menu(call, 'Вы находитесь в разделе выбора города для подписки на прогноз погоды: ', subscriber, cities)
    # Обработка города для подписки на прогноз погоды
    elif call.data.startswith('citySubscribe_'):
        city_id = call.data.split('_')[1]
        print(f"{now} Нажата кнопка id={city_id} для добавления города для прогноза погоды")
        cities = City.objects.all()
        city = cities.filter(id=city_id).first()
        if city is None:
            print(f"{now} Город с id={city_id} не найден")
            return
        print(f"{now} Получена город {city} для подписки на прогноз погоды")
        username = call.message.chat.username if call.message.chat.username else "Неизвестный пользователь"
        subscriber, created = TelegramSubscriber.objects.get_or_create(chat_id=call.message.chat.id, defaults={'username': username})
        print(f"{now} Получен пользователь {subscriber.username} для добавления подписки на прогноз погоды")
        subscriber.subscribed_weather_city.add(city)
        subscriber.weather_sent = True
        subscriber.save()
        print(f"{now} Добавлен город {city} для прогноза погоды для пользователя {subscriber.username}")
        subscribe_weather_menu(call, f"Добавлен город {city}", subscriber, cities)
    # Обработка ветки отписки нот прогноза погоды
    elif call.data == 'key4':
        subscriber = TelegramSubscriber.objects.filter(chat_id=call.message.chat.id).first()
        cities = subscriber.subscribed_weather_city.all()
        unsubscribe_weather_menu(call, 'Вы находитесь в разделе выбора города для отписки от прогноза погоды.', subscriber, cities)
    # Обработка города для отписки на прогноз погоды
    elif call.data.startswith('cityUnsubscribe_'):
        city_id = call.data.split('_')[1]
        print(f"{now} Нажата кнопка id={city_id} для удаления города для отписки от прогноза погоды")
        city = City.objects.filter(id=city_id).first()
        if city:
            print(f"{now} Получен город {city} для удаления из подписки на прогноз погоды пользователя")
            subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
            print(f"{now} Получен пользователь {subscriber.username} для удаления из подписки")
            subscriber.subscribed_weather_city.remove(city)
            if not subscriber.subscribed_to_categories.exists():
                subscriber.weather_sent = False  # Отписка от прогноза погоды
            subscriber.save()
            print(f"{now} Удаление города {city} из подписки на прогноз погоды пользователя {subscriber.username}")
            cities = subscriber.subscribed_weather_city.all()
            unsubscribe_weather_menu(call, f'Вы отписались от прогноза погоды на город: {city.city_name}', subscriber, cities)
    #добавить ветку валюты
    elif call.data == 'key5':
        keyboard_category = types.InlineKeyboardMarkup(row_width=1)
        keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
        #bot.send_message(call.message.chat.id, f'Вы находитесь в разделе подписки на курсы валют ', reply_markup=keyboard_category)
        bot.edit_message_text(f'Вы находитесь в разделе подписки на курсы валют ', call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)

    elif call.data == 'key6':
        keyboard_category = types.InlineKeyboardMarkup(row_width=1)
        keyboard_category.add(types.InlineKeyboardButton('Назад', callback_data='key0'))
        #bot.send_message(call.message.chat.id, f'Вы находитесь в разделе отписки от курсов валют ', reply_markup=keyboard_category)
        bot.edit_message_text(f'Вы находитесь в разделе отписки от курсов валют ', call.message.chat.id, call.message.message_id, reply_markup=keyboard_category)
    #добавить ветку рассылки
    elif call.data == 'key7':
        print(f"{now} Нажата кнопка {call.data} для настройки рассылки сообщений")
        # Получаем подписчика
        #from news.models import TelegramSubscriber
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        settings_menu(call, 'Вы находитесь в настройках рассылки сообщений.', subscriber)
    elif call.data.startswith('news_sent_on'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки новостей")
        subscriber.news_sent = True  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки новостей для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку новостей', subscriber)
    elif call.data.startswith('news_sent_off'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для отключения рассылки новостей")
        subscriber.news_sent = False  # Отписка от новостей
        subscriber.save()
        print(f"{now} Отключение рассылки новостей для пользователя {subscriber.username}")
        settings_menu(call, 'Вы отключили рассылку новостей.', subscriber)
    elif call.data.startswith('currency_sent_on'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки курса валют")
        subscriber.currency_sent = True  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки курса валют для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку курса валют.', subscriber)
    elif call.data.startswith('currency_sent_off'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для отключения рассылки курса валют")
        subscriber.currency_sent = False  # Отписка от новостей
        subscriber.save()
        print(f"{now} Отключение рассылки курса валют для пользователя {subscriber.username}")
        settings_menu(call, 'Вы отключили рассылку курса валют.', subscriber)
    elif call.data.startswith('weather_sent_on'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки прогноза погоды")
        subscriber.weather_sent = True  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки прогноза погоды для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку прогноза погоды', subscriber)
    elif call.data.startswith('weather_sent_off'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для отключения рассылки прогноза погоды")
        subscriber.weather_sent = False  # Отписка от новостей
        subscriber.save()
        print(f"{now} Отключение рассылки прогноза погоды для пользователя {subscriber.username}")
        settings_menu(call, 'Вы отключили рассылку прогноза погоды', subscriber)
    elif call.data.startswith('full'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения полных сообщений рассылки")
        subscriber.message_format = "full"  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение полных сообщений рассылки для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили полные сообщений рассылки', subscriber)
    elif call.data.startswith('short'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения сокращенных сообщений рассылки")
        subscriber.message_format = 'short'  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение сокращенных сообщений рассылки для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили сокращенных сообщений рассылки', subscriber)
    elif call.data.startswith('every_hour'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки новостей каждый час")
        subscriber.frequency_sending = 'every_hour'  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки новостей каждый час для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку новостей каждый час', subscriber)
    elif call.data.startswith('every_3hour'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки новостей каждые 3 часа")
        subscriber.frequency_sending = 'every_3hour'  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки новостей каждые 3 часа для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку новостей каждые 3 часа', subscriber)
    elif call.data.startswith('every_6hour'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки каждые 6 часов новостей")
        subscriber.frequency_sending = 'every_6hour'  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки новостей каждые 6 часов для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку каждые 6 часов новостей', subscriber)
    elif call.data.startswith('every_9hour'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки каждые 9 часов новостей")
        subscriber.frequency_sending = 'every_9hour'  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки новостей каждые 9 часов для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку новостей каждые 9 часов', subscriber)
    elif call.data.startswith('every_12hour'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения рассылки новостей каждые 12 часов")
        subscriber.frequency_sending = 'every_12hour'  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение рассылки новостей каждые 12 часов для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили рассылку каждые 12 часов новостей', subscriber)
    elif call.data.startswith('daily'):
        subscriber = TelegramSubscriber.objects.get(chat_id=call.message.chat.id)
        print(f"{now} Получен пользователь {subscriber.username} для включения ежедневной новостей")
        subscriber.frequency_sending = 'daily'  # Отписка от новостей
        subscriber.save()
        print(f"{now} Включение ежедневной рассылки новостей для пользователя {subscriber.username}")
        settings_menu(call, 'Вы включили ежедневную рассылку новостей', subscriber)
#убрать после перехода на расширенную подписку
def send_news():
    from news.models import TelegramSubscriber, News  # Отложенный импорт здесь
    today = datetime.date.today()
    subscribers = TelegramSubscriber.objects.all()
    # news = News.objects.filter(date=today, is_published=True, is_sent=False)
    news = News.objects.filter(is_published=True, is_sent=False)
    print(f"{now} Найдено новостей для отправки: {news.count()}")
    #logging.info(f"Найдено новостей для отправки: {news.count()}")

    if news.exists():
        for article in news:
            if not article.is_sent:
                # добавляем стилизацию категории новости
                category = article.cat.name  # Извлекаем название категории
                category_styles = {
                    'Безопасность': '🔒',
                    'Статьи': '📄',
                    'Обзоры': '🔍',
                    'Интервью': '🗣️',
                }
                # делаем обрезание полей в сообщении
                author = trim_author(article.author)
                content = trim_content(article.content, word_limit=35)
                category_style = category_styles.get(category, 'ℹ️')  # Используем нейтральный символ
                print(f"{now} Отправляем новость: {article.title}")
                #logging.info(f"Отправляем новость: {article.title}")
                # собираем сообщение
                message = f'{category_style} <b>{category} {article.date}</b>\n\n' \
                        f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n' \
                        f'{content}\n' \
                        f'{author}'
                        # f'{article.author}'

                #цикл отправки сообщений по пользователям с переотправлением в случае ошибок
                for subscriber in subscribers:
                    image = article.image if article.image else None
                    success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
                    if not success:
                        print(f"{now} Ошибка при отправке сообщения пользователю {subscriber.username}: повторные попытки не увенчались успехом")
                        #logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.username}: повторные попытки не увенчались успехом")
                #после отправки сообщений помечаем новость как отправленную
                article.is_sent = True
                print(f"{now} Новость {article.title} помечена как отправленная.")
                #logging.info(f"Новость {article.title} помечена как отправленная.")
                article.save()
    else:
        for subscriber in subscribers:
            try:
                # bot.send_message(subscriber.chat_id, "На данный момент свежих новостей нет.")
                print(f"{now} Отправка сообщения пользователю {subscriber.username}: Новых сообщений нет")
                #logging.info(f"Отправка сообщения пользователю {subscriber.username}: Новых сообщений нет")
            except Exception as e:
                print(f"{now} Ошибка при отправке сообщения пользователю {subscriber.username}: {e}")
                #logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.username}: {e}")

#запуск бота через supervisord
def run_bot():
    print(f"{now} Запуск Telegram-бота...")
    #logging.info("Запуск Telegram-бота...")
    # bot.polling(none_stop=True)
    try:
        #bot.polling(none_stop=True)
        # Запуск polling с настройкой тайм-аутов
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"{now} Ошибка: {e}")
        #logging.info(f"Ошибка: {e}")

if __name__ == "__main__":
    run_bot()


# убрал чтобы запуск шел через Supervisor.
# if __name__ == "__main__":
#     try:
#         run_bot()
#     except Exception as e:
#         print(f"Ошибка при запуске бота: {e}")