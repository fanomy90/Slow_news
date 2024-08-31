import os
import uuid  # для генерации случайных имен файлов
from django.utils.timezone import now
import json
from datetime import datetime, timedelta
import re
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils.text import slugify
import requests
from bs4 import BeautifulSoup
from django.core.management import call_command

from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings
# from news.tasks import send_task_status
import asyncio
from channels.layers import get_channel_layer

url = 'https://cisoclub.ru/category/news/'
base_url = 'https://cisoclub.ru'
now = datetime.now()
output_dir = '/app/puppeteer/SAVE'
output_path = os.path.join(output_dir, 'news.json')
output_path_history = os.path.join(output_dir, 'news_history.json')

# обработка для передачи сообщений от задачи
async def send_task_status(task_id, status, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(f"task_{task_id}", {"type": "task_status", "status": status, "message": message,})

def load_existing_data(file_path):
    print(str(now) + ' получим исторические данные')
    try:
        call_command('dumpdata', 'news', indent=2, output=file_path)
        print(str(now) + ' получены исторически данные: ' + file_path)
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(str(now) + ' получение исторических данных завершилось с ошибкой: ' + str(e))
        return []

def get_max_pk(data):
    max_pk = 0
    for item in data:
        if 'pk' in item and isinstance(item['pk'], int) and item['pk'] > max_pk:
            max_pk = item['pk']
    return max_pk

def get_existing_titles(data):
    titles = set()
    for item in data:
        if item['model'] == 'news.news' and 'fields' in item and 'title' in item['fields']:
            titles.add(item['fields']['title'])
    return titles

def parse_date(date_str):
    date_str = date_str.strip()
    print(f'Парсинг даты: {date_str}')

    if not date_str:
        print('Дата не найдена, возвращаем None')
        return None

    if 'timeago' in date_str:
        datetime_match = re.search(r'datetime="([^"]+)"', date_str)
        if datetime_match:
            datetime_str = datetime_match.group(1)
            try:
                datetime_str = datetime_str.split(' GMT')[0]
                parsed_date = datetime.strptime(datetime_str, '%a %b %d %Y %H:%M:%S')
                return parsed_date.date()
            except ValueError as e:
                print(f'Ошибка парсинга времени из timeago: {e}')
                return None
    # проверка часов нгазад
    hours_ago_match = re.search(r'(\d+)\sчас(а|ов)\sназад', date_str)
    if hours_ago_match:
        hours_ago = int(hours_ago_match.group(1))
        return (datetime.now() - timedelta(hours=hours_ago)).date()
    # проверка на время
    time_match = re.search(r'\b\d{2}:\d{2}\b', date_str)
    if time_match:
        print('проверка на Время')
        return datetime.now().date()
    # проверка на сегодня
    if "Сегодня" in date_str:
        print('проверка на Сегодня')
        return datetime.now().date()
    # проверка на вчера
    if "Вчера" in date_str:
        print('проверка на Вчера')
        return (datetime.now() - timedelta(days=1)).date()
    # проверка на формат типа "26 июля"
    month_mapping = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }
    date_match = re.search(r'(\d{1,2})\s([а-яА-Я]+)', date_str)
    if date_match:
        print('проверка на Дату формата "дд месяц"')
        day = int(date_match.group(1))
        month_str = date_match.group(2)
        month = month_mapping.get(month_str)
        if month:
            year = datetime.now().year
            return datetime(year, month, day).date()

    # Проверка на формат "дд.мм.гггг" (например, 21.12.2023)
    dot_date_match = re.search(r'\b(\d{2})\.(\d{2})\.(\d{4})\b', date_str)
    if dot_date_match:
        print('проверка на Формат ДД.ММ.ГГГГ')
        day = int(dot_date_match.group(1))
        month = int(dot_date_match.group(2))
        year = int(dot_date_match.group(3))
        return datetime(year, month, day).date()

    print(f'Не удалось распознать дату: {date_str}')
    return None

# @shared_task(bind=True)
# def cisoclub_news(task_id):
def cisoclub_news(task_id):
    print(str(now) + ' запущена задача с id: ' + task_id)
    # asyncio.get_event_loop().run_until_complete(
    #     send_task_status(task_id.request.id, "PROGRESS", f"{now} Запущена задача cisoclub_news")
    # )
    # Запуск асинхронного процесса для отправки статуса задачи
    async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} Запущена задача cisoclub_news")
    
    if not os.path.exists(output_dir):
        print(str(now) + ' не найдена директория для сохранения: ' + output_dir)
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125'
        }

        existing_data = load_existing_data(output_path_history)
        max_existing_pk = get_max_pk(existing_data)
        existing_titles = get_existing_titles(existing_data)

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            src = response.text
            soup = BeautifulSoup(src, 'lxml')
            post_wrappers = soup.find_all("div", class_='postWrapper')
            news_links = []
            news_data = []
            # base_url = 'https://cisoclub.ru'
            news_pk = max_existing_pk + 1
            categories = {
                "model": "news.category",
                "pk": 1,
                "fields": {
                    "name": "Безопасность",
                    "slug": "security"
                }
            }
            data = [categories] if not existing_data else []
            for wrapper in post_wrappers:
                a_tags = wrapper.find_all('a', href=True)
                for a_tag in a_tags:
                    href = a_tag['href']
                    if not href.startswith('/category/') and not href.startswith('/author/'):
                        full_url = base_url + href
                        news_links.append(full_url)

            print('получены ссылки для анализа: ' + ', '.join(news_links))
            async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} получены ссылки для анализа: {(news_links)}")
            # инициализация счетчика новостей доступных для импорта
            news_count = 0
            # инициализация счетчика дубликатов новостей для лога
            dublicate_count = 0
            for news_link in news_links:
                post_response = requests.get(news_link, headers=headers)
                if post_response.status_code == 200:
                    post_src = post_response.text
                    post_soup = BeautifulSoup(post_src, 'lxml')

                    post_date_div = post_soup.find("div", class_='postDate')
                    if post_date_div:
                        date_str = post_date_div.text
                        timeago_tag = post_date_div.find('timeago')
                        if timeago_tag:
                            date_str = str(timeago_tag)
                    else:
                        date_str = ''

                    date = parse_date(date_str)

                    if date is None:
                        print(f'Пропуск новости с некорректной датой: {date_str}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'Пропуск новости с некорректной датой: {date_str}')
                        continue  # Пропускаем новость с некорректной датой

                    title = post_soup.find("h1", class_='postContentTitle')
                    if title:
                        title = title.text
                    else:
                        print(f'Пропуск новости без заголовка: {news_link}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'Пропуск новости без заголовка: {news_link}')
                        continue  # Пропускаем новость без заголовка

                    content = post_soup.find("div", class_='articleContent')
                    if content:
                        content = content.text
                    else:
                        print(f'Пропуск новости без содержания: {news_link}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'Пропуск новости без содержания: {news_link}')
                        continue  # Пропускаем новость без содержания

                    author = post_soup.find("div", class_='author_info_text')
                    if author:
                        author = author.text
                    else:
                        print(f'Пропуск новости без автора: {news_link}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'Пропуск новости без автора: {news_link}')
                        continue  # Пропускаем новость без автора

                    image = post_soup.find("div", class_='imageWrapper')
                    if image:
                        image2 = image.find('img', src=True)
                        if image2:
                            image_url = base_url + image2['src']
                        else:
                            image_url = None
                    else:
                        image_url = None

                    slug = news_link.replace('https://', '').replace('/', '').replace('.', '-')
                    if title not in existing_titles:
                        news_post = {
                            "model": "news.news",
                            "pk": news_pk,
                            "fields": {
                                "title": title,
                                "slug": slug,
                                "content": content,
                                "time_create": datetime.now().isoformat(),
                                "time_update": datetime.now().isoformat(),
                                "is_published": True,
                                "cat": 1,
                                "date": date.isoformat(),
                                "author": author,
                                "image": image_url
                            }
                        }
                        data.append(news_post)
                        news_pk += 1
                        news_count += 1
                    else:
                        dublicate_count += 1
                        print(f'Дубликат найден и пропущен: {title}')
                        # async_to_sync(send_task_status)(task_id, "PROGRESS", f'{now} Дубликат найден и пропущен: {title}')
                else:
                    print('полученная ссылка: ' + str(news_link) + ' не доступна для анализа')
                    async_to_sync(send_task_status)(task_id, "PROGRESS", f'{now} полученная ссылка: {str(news_link)} не доступна для анализа')
                    return False
        else:
            print('ссылка сайта: ' + str(base_url) + ' не доступна для анализа')
            async_to_sync(send_task_status)(task_id, "PROGRESS", f'ссылка сайта: ' + str(base_url) + ' не доступна для анализа')
            return False

        async_to_sync(send_task_status)(task_id, "PROGRESS", f'{now} Было обнаружено {dublicate_count} дубликатов новостей которые не будут сохранены в файл для импорта')
        
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
            # print(str(now) + ' посты новостей cisoclub сохранены в файл: ' + str(output_path))
            # message = f"{now} посты новостей cisoclub сохранены в файл: {output_path}"
            # async_to_sync(send_task_status)(task_id, "PROGRESS", message)

            # asyncio.get_event_loop().run_until_complete(
            #     send_task_status(task_id.request.id, "PROGRESS", f"{now} посты новостей cisoclub сохранены в файл: {output_path}")
            # )
            # Отправляем сообщение о завершении задачи
            async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} в файл: {output_path} сохранено {news_count} постов новостей cisoclub которые можно импортировать")

        return True
    except Exception as e:
        print(str(now) + ' получение новостей с сайта cisoclub завершилось с ошибкой: ' + str(e))
        return f'An error occurred: {e}'
