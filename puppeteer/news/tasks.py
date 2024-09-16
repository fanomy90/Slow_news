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
from django.utils.timezone import now

import os
from celery import shared_task
from django.core.management import call_command #возможный косяк из за чего не запускались команды
from django.conf import settings #для генерации имен файлов
import logging

from puppeteer.celery import app

logger = logging.getLogger(__name__)
# обработка для передачи сообщений от задачи
async def send_task_status(task_id, status, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(f"task_{task_id}", {"type": "task_status", "status": status, "message": message,})

@shared_task(bind=True)
def download_a_news(self):
    # task_id = download_a_news.request.id
    # cisoclub_news(task_id)
    # Отправляем статус через универсальную функцию
    asyncio.get_event_loop().run_until_complete(
        send_task_status(self.request.id, "PROGRESS", "запущена задача download_a_news из tasks.py")
    )
    cisoclub_news(self.request.id, "security")
    return True

@app.task()
def download_a_news_beat(self):
    cisoclub_news(self.request.id, "security")
    return True

@shared_task(bind=True)
def import_news_task(self):
    input_dir = settings.BASE_DIR / 'SAVE'
    input_path = input_dir / 'news.json'
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
        async_to_sync(send_task_status)(self.request.id, "PROGRESS", f"{now} в файл: {output_path} сохранено {news_count} постов новостей cisoclub которые можно импортировать")
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