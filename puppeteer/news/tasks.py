import requests as r
import uuid #случайные имена файлов
import time
from celery import shared_task
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
from news  .models import News, Category
from django.utils.text import slugify

from news.management.commands import load_test3

# Задача парсинга
url = 'https://cisoclub.ru/category/news/'
@shared_task()
def download_a_news():
    
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125'
    }
    href = []
    session = r.Session()
    session.headers = headers
    page = session.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    links = soup.find_all('h3', class_='entry-title')
    posts = []

    for link in links:
        href = link.a.get('href')
        posts.append(href)

    news_data = []
    #Проверка для какой категории новости
    if 'economics' in url:
        cat_id = 6
        category_name = "Экономика"
        category_slug = "economics"
    elif 'politics' in url:
        cat_id = 7
        category_name = "Политика"
        category_slug = "politics"
    elif 'cisoclub.ru' in url:
        cat_id = 1
        category_name = "Безопасность"
        category_slug = "security"
    else:
        cat_id = 999  # Set a default value if the category cannot be determined from the URL
        category_name = "Other"
        category_slug = "other"

    for line in posts:
        page2 = session.get(line)
        soup2 = BeautifulSoup(page2.text, 'lxml')
        allNewsTitle = soup2.find('title').text
        allNewsPreview = soup2.find('div', class_='entry-content').text
        picNews = soup2.find('div', class_='photoandcap').a.get('href')
        linkNews = line

        title = allNewsTitle
        content = allNewsPreview
        photo_url = picNews

        #photo_filename = extract_image_filename(photo_url)
        photo_filename = photo_url.split('/')[-1]

        # Form the slug from the last part of the URL without the file extension
        #slug = linkNews.replace("/", "-")
        slug = linkNews.replace('https://', '').replace('/', '').replace('.', '-')

        woman_data = {
            "title": title,
            "slug": slug,
            "content": content,
            #"photo": f"C:\\test\\{photo_filename}",
            "cat_id": cat_id
        }
        news_data.append(woman_data)

    # Categories data (you can modify this part as needed)
    categories = [
        {"name": category_name, "slug": category_slug}
    ]

    # Combine categories and news data into the final structure
    data = {
        "categories": categories,
        "news": news_data
    }

    # Save the data as a JSON file with UTF-8 encoding
    file_name_news = settings.BASE_DIR / 'SAVE' / 'news.json'

    #with open('/home/skiner/site/puppeteer/news.json', 'w', encoding='utf-8') as json_file:
    with open(file_name_news, 'w', encoding='utf-8') as json_file:

        json.dump(data, json_file, ensure_ascii=False, indent=2)
        now = datetime.datetime.now()
        print(str(now) + ' parse cisoclub complete')
    return True
    #return f"{now} parse cisoclub complete"

@shared_task()
def import_news_task():
    load_test3.Command().handle()
    #now = datetime.datetime.now()
    #return f"{now} import cisoclub complete"
    return True



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