import requests as r
import uuid #случайные имена файлов
import time
from django.conf import settings #для генерации имен файлов
from random import randint
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import asyncio
import json
import datetime
from bs4 import BeautifulSoup
#для импорта новостей
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils.text import slugify
# from news.management.commands import load_test3
from news.task.parser_cisoclub import cisoclub_news
from news.task.parser_cisoclub_beat import cisoclub_news_beat

from news.task.slow_bot_news import send_news_frequency

from django.utils.timezone import now

import os
from celery import shared_task
from django.core.management import call_command #возможный косяк из за чего не запускались команды
from django.conf import settings #для генерации имен файлов
import logging

from puppeteer.celery import app

#для бота
# from news.models import News
from .slow_bot import run_bot, send_news
import subprocess
from celery.exceptions import MaxRetriesExceededError
from requests.exceptions import Timeout  # Импорт тайм-аута

logger = logging.getLogger(__name__)
# обработка для передачи сообщений от задачи
async def send_task_status(task_id, status, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(f"task_{task_id}", {"type": "task_status", "status": status, "message": message,})

@shared_task(bind=True)
def download_a_news_beat(self):
    # Отправляем статус через универсальную функцию
    asyncio.get_event_loop().run_until_complete(
        send_task_status(self.request.id, "PROGRESS", "запущена SQL задача cisoclub_news_beat из tasks.py")
    )
    print("Запущена фоновая SQL задача парсинга и иморта новостей категории security")
    # cisoclub_news.apply_async(kwargs={'mode': 'security'}, task_id=self.request.id)
    cisoclub_news_beat.apply_async(kwargs={'mode': 'security'}, task_id=self.request.id)
    print("Выполнена фоновая SQL задача парсинга и импорт новостей категории security.")
    # Задержка на 20 секунд
    # time.sleep(20)
    #print("Выполнена фоновая задача парсинга новостей категории security. Запускаем импорт полученных новостей...")
    # import_news_task.delay()  # Запуск import_news_task как асинхронной задачи
    # print("Выполнен импорт полученных новостей.")
    return True

# @app.task()
# def download_a_news_beat(self):
#     cisoclub_news(self.request.id, "security")
#     return True

# @shared_task(bind=True)
# def download_a_news_beat(self):
#     print("Запуск фоновой задачи парсинга новостей категории security")
#     task_id = self.request.id
#     async_to_sync(send_task_status)(task_id, "START", "Запуск парсинга новостей.")
#     result = cisoclub_news(self.request.id, "security")

#     cisoclub_news.apply_async(kwargs={'mode': 'security'}, task_id=task_id)

#     async_to_sync(send_task_status)(task_id, "END", "Парсинг завершен.")
#     print("Выполнена фоновая задача парсинга новостей категории security")
#     # Запускаем другую задачу после завершения парсинга
#     # print("Запуск фоновой задачи импорта новостей категории security")
#     # async_to_sync(send_task_status)(task_id, "START", "Запуск импорта новостей.")
#     # import_news_task.delay()  # Запуск import_news_task как асинхронной задачи
#     # async_to_sync(send_task_status)(task_id, "END", "Иморт завершен.")
#     # print("Выполнена фоновая задача импорта новостей категории security")
#     return result
    

@shared_task(bind=True)
def import_news_task(self):
    # input_dir = settings.BASE_DIR / 'SAVE'
    # input_path = input_dir / 'news.json'

    input_dir = '/yt/puppeteer/SAVE'
    input_path = os.path.join(input_dir, 'news.json')


    # Логирование пути к файлу
    # logger.info(f'Checking if file exists: {input_path}')
    print(f'Checking if file exists: {input_path}')
    async_to_sync(send_task_status)(self.request.id, "PROGRESS", f"{now} поиск файла {input_path} с новостными постами")
    if not os.path.exists(input_path):
        # logger.error(f'File {input_path} not found')
        print(f'File {input_path} not found')
        async_to_sync(send_task_status)(self.request.id, "PROGRESS", f"{now} файл с новостными постами {input_path} не был найден ")
        return f'File {input_path} not found'
    try:
        # Логирование перед вызовом команды
        # logger.info(f'Calling command to load data from {input_path}')
        print(f'Calling command to load data from {input_path}')
        async_to_sync(send_task_status)(self.request.id, "PROGRESS", f"{now} запущен импорт файла {input_path} в базу данных")
        call_command('loaddata', str(input_path))  # Приведение к строке для call_command
        # logger.info('Data loaded successfully')
        print('Data loaded successfully')
        async_to_sync(send_task_status)(self.request.id, "PROGRESS", f"{now} импорт файла {input_path} в базу данных прошел успешно")
        return 'Data loaded successfully'
    except Exception as e:
        # logger.error(f'An error occurred: {e}')
        print(f'An error occurred: {e}')
        async_to_sync(send_task_status)(self.request.id, "ERROR", f'An error occurred: {e}')
        return f'An error occurred: {e}'

@shared_task
def cpu_task1():
    time_to_sleep = randint(5, 10)
    time.sleep(time_to_sleep)
    return True

@shared_task(bind=True)
def cpu_task2(self):
    try:
        # Время ожидания перед выполнением задачи
        time_to_sleep = randint(5, 10)
        
        for i in range(time_to_sleep):
            time.sleep(1)
            self.update_state(state="PROGRESS", meta={"current": i, "total": time_to_sleep})
            
            # Отправляем статус через универсальную функцию
            asyncio.get_event_loop().run_until_complete(
                send_task_status(self.request.id, "PROGRESS", f"I slept for {i + 1} seconds")
            )
        
        # По завершении задачи отправляем сообщение о её успехе
        return {"current": time_to_sleep, "total": time_to_sleep, "status": "SUCCESS"}
    
    except Exception as e:
        self.update_state(state="FAILURE", meta=str(e))
        asyncio.get_event_loop().run_until_complete(
            send_task_status(self.request.id, "FAILURE", f"An error occurred: {str(e)}")
        )
        return {"status": "FAILURE", "message": str(e)}


# Задачи для телеграм бота
# @shared_task
# def tel_daily_news():
#     today = datetime.date.today()
#     news = News.objects.filter(date=today, is_published=True)

#     for article in news:
#         message = f"Заголовок: {article.title}\nСсылка: {article.get_absolute_url()}\nАвтор: {article.author}"
#         send_news_to_tel(message)
@shared_task
def send_daily_news():
    #today = datetime.date.today()
    #news = News.objects.filter(date=today, is_published=True, is_sent=False)  # Фильтруем только те новости, которые не были отправлены
    
    # if news.exists():
    #     send_news(news)
    # Отправляем новости или сообщение об их отсутствии
    send_news()

@shared_task
def send_news_every_hour():
    send_news_frequency("every_hour")
@shared_task
def send_news_every_3hour():
    send_news_frequency("every_3hour")
@shared_task
def send_news_every_6hour():
    send_news_frequency("every_6hour")
@shared_task
def send_news_every_9hour():
    send_news_frequency("every_9hour")
@shared_task
def send_news_every_12hour():
    send_news_frequency("every_12hour")
@shared_task
def send_news_daily():
    send_news_frequency("daily")

# @shared_task
# def start_telegram_bot():
#     run_bot()

# @shared_task
# def run_bot():
#     print("Запуск Telegram-бота...")
#     bot.polling(none_stop=True)

# @shared_task
# def run_bot():
    # subprocess.Popen(['python', 'news/slow_bot.py'])

# @shared_task(bind=True, autoretry_for=(subprocess.SubprocessError,), retry_kwargs={'max_retries': 5, 'countdown': 10})
# def run_bot(self):
#     try:
#         # Запуск бота через Popen
#         subprocess.Popen(['python', 'news/slow_bot.py'])
#     except subprocess.SubprocessError as exc:
#         # Если возникает ошибка при запуске процесса, задача повторяется
#         raise self.retry(exc=exc)
#     except MaxRetriesExceededError:
#         # Обработка случая, если превышено количество попыток
#         print("Превышено максимальное количество попыток запуска бота")
#         return "Max retries exceeded"

# убрал чтобы запуск шел через Supervisor.
# @shared_task(bind=True, autoretry_for=(Timeout,), retry_kwargs={'max_retries': 5, 'countdown': 10})
# def run_bot(self):
#     try:
#         # subprocess.Popen(['python', 'news/slow_bot.py'])
#         # Запуск бота как отдельного процесса
#         subprocess.Popen(['python', 'news/slow_bot.py'], start_new_session=True)
#     except Timeout as exc:
#         raise self.retry(exc=exc)
#     except MaxRetriesExceededError:
#         print("Превышено максимальное количество попыток запуска бота")
#         return "Max retries exceeded"