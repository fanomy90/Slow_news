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
from news.management.commands import load_test3
from news.task.parser2 import parser_test
from news.task.parser_cisoclub import cisoclub_news

import os
from celery import shared_task
from django.core.management import call_command #возможный косяк из за чего не запускались команды
from django.conf import settings #для генерации имен файлов
import logging

logger = logging.getLogger(__name__)

@shared_task()
def download_a_news():
    #parser_test()
    cisoclub_news()
    return True

@shared_task
def import_news_task():
    input_dir = settings.BASE_DIR / 'SAVE'
    input_path = input_dir / 'news.json'
    
    # Логирование пути к файлу
    # logger.info(f'Checking if file exists: {input_path}')
    print(f'Checking if file exists: {input_path}')
    
    if not os.path.exists(input_path):
        # logger.error(f'File {input_path} not found')
        print(f'File {input_path} not found')
        return f'File {input_path} not found'
    
    try:
        # Логирование перед вызовом команды
        # logger.info(f'Calling command to load data from {input_path}')
        print(f'Calling command to load data from {input_path}')
        call_command('loaddata', str(input_path))  # Приведение к строке для call_command
        # logger.info('Data loaded successfully')
        print('Data loaded successfully')
        return 'Data loaded successfully'
    except Exception as e:
        # logger.error(f'An error occurred: {e}')
        print(f'An error occurred: {e}')
        return f'An error occurred: {e}'



# тестовые задачи для проверки работы вебсокетов
CAT_URL = "https://cataas.com/cat"
@shared_task
def download_a_cat():
    resp = r.get(CAT_URL)
    file_ext = resp.headers.get('Content-Type').split('/')[1]
    file_name = settings.BASE_DIR / 'SAVE' / (str(uuid.uuid4()) + "." + file_ext)
    with open(file_name, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=128):
            f.write(chunk)
    return True
@shared_task
def cpu_task1():
    time_to_sleep = randint(5, 10)
    time.sleep(time_to_sleep)
    return True



# нерабочий пример задачи с передачей сообщений статуса
# @shared_task(bind=True)
# def cpu_task2(self):
#     try:
#         async def send_task_status():
#             channel_layer = get_channel_layer()
#             await channel_layer.group_send(
#                 f"task_{self.request.id}",
#                 {"type": "task_status", "status": "PROGRESS", "message": f"I slept for {i + 1} seconds"},
#             )
#         time_to_sleep = randint(5, 10)
#         for i in range(time_to_sleep):
#             time.sleep(1)
#             self.update_state(state="PROGRESS", meta={"current": i, "total": time_to_sleep})
#             asyncio.get_event_loop().run_until_complete(send_task_status())
#         return {"current": time_to_sleep, "total": time_to_sleep, "status": "SUCCESS"}
#     except Exception as e:
#         self.update_state(state="FAILURE", meta=str(e))
#         return {"status": "FAILURE", "message": str(e)}