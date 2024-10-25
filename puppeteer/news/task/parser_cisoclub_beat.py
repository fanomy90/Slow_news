import os
import uuid  # для генерации случайных имен файлов
from django.utils.timezone import now, make_aware
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

from django.db.models import Max
# from news.models import News
from django.db import transaction
import time

base_url = 'https://cisoclub.ru'
now = datetime.now()
# output_dir = '/app/puppeteer/SAVE'
output_dir = '/yt/puppeteer/SAVE'
output_path = os.path.join(output_dir, 'news.json')
output_path_history = os.path.join(output_dir, 'news_history.json')

# обработка для передачи сообщений от задачи
async def send_task_status(task_id, status, message):
    channel_layer = get_channel_layer()
    #await channel_layer.group_send(f"{now} task_{task_id}", {"type": "task_status", "status": status, "message": message,})
    await channel_layer.group_send(f"task_{task_id}", {"type": "task_status", "status": status, "message": message,})

# получение максимального pk новостных записей напрямую из бд
def get_max_pk():
    from news.models import News
    max_pk = News.objects.aggregate(Max('pk'))['pk__max']
    print(str(now) + ' получение max_pk из БД ' + str(max_pk))
    return max_pk if max_pk is not None else 0

# получение заголовков новостей напрямую из бд
def get_existing_titles():
    from news.models import News
    existing_titles = News.objects.values_list('title', flat=True)
    return list(existing_titles)

# обработка даты
def aware_date(naive_datetime):
    # Преобразование наивной даты в "сознательную"
    aware_datetime = make_aware(naive_datetime)
    return aware_datetime

def parse_date(date_str):
    date_str = date_str.strip()
    print(f'{now} Парсинг даты: {date_str}')
    if not date_str:
        print(f'{now} Дата не найдена, возвращаем None')
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
                print(f'{now} Ошибка парсинга времени из timeago: {e}')
                return None
    # проверка часов нгазад
    hours_ago_match = re.search(r'(\d+)\sчас(а|ов)\sназад', date_str)
    if hours_ago_match:
        hours_ago = int(hours_ago_match.group(1))
        return (datetime.now() - timedelta(hours=hours_ago)).date()
    # проверка на время
    time_match = re.search(r'\b\d{2}:\d{2}\b', date_str)
    if time_match:
        print(f'{now} проверка на Время')
        return datetime.now().date()
    # проверка на сегодня
    if "Сегодня" in date_str:
        print(f'{now} проверка на Сегодня')
        return datetime.now().date()
    # проверка на вчера
    if "Вчера" in date_str:
        print(f'{now} проверка на Вчера')
        return (datetime.now() - timedelta(days=1)).date()
    # проверка на формат типа "26 июля"
    month_mapping = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }
    date_match = re.search(r'(\d{1,2})\s([а-яА-Я]+)', date_str)
    if date_match:
        print(f'{now} проверка на Дату формата "дд месяц"')
        day = int(date_match.group(1))
        month_str = date_match.group(2)
        month = month_mapping.get(month_str)
        if month:
            year = datetime.now().year
            return datetime(year, month, day).date()

    # Проверка на формат "дд.мм.гггг" (например, 21.12.2023)
    dot_date_match = re.search(r'\b(\d{2})\.(\d{2})\.(\d{4})\b', date_str)
    if dot_date_match:
        print(f'{now} проверка на Формат ДД.ММ.ГГГГ')
        day = int(dot_date_match.group(1))
        month = int(dot_date_match.group(2))
        year = int(dot_date_match.group(3))
        return datetime(year, month, day).date()

    print(f'{now} Не удалось распознать дату: {date_str}')
    return None

#@shared_task(bind=True)
@shared_task(bind=True, time_limit=60, soft_time_limit=30)
# def cisoclub_news(task_id):
# def cisoclub_news(task_id, mode = "security"):
def cisoclub_news_beat(self, mode=None):
    
    task_id = self.request.id
    # Запуск асинхронного процесса для отправки статуса задачи
    
    if not os.path.exists(output_dir):
        print(str(now) + ' не найдена директория для сохранения: ' + output_dir)
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125'
        }
        # получение данных напрямую из БД
        max_existing_pk = get_max_pk()
        existing_titles = get_existing_titles()

        # # сделать привязку к разным разделам
        if mode == "security":
            url = 'https://cisoclub.ru/category/news/'
            categoriesPk = 1
            categoriesName = "Безопасность"
            categoriesSlug = "security"
        if mode == "public":
            url = 'https://cisoclub.ru/category/public/'
            categoriesPk = 3
            categoriesName = "Статьи"
            categoriesSlug = "public"
        if mode == "review":
            url = 'https://cisoclub.ru/category/obzory/'
            categoriesPk = 4
            categoriesName = "Обзоры"
            categoriesSlug = "obzory"
        if mode == "interviews":
            url = 'https://cisoclub.ru/category/interviews/'
            categoriesPk = 5
            categoriesName = "Интервью"
            categoriesSlug = "interviews"
        print(str(now) + ' запущена задача ипорта новостей категории ' + categoriesName + ' с id: ' + task_id)
        # Пауза для обеспечения отправки сообщения
        # time.sleep(2)
        async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} Запущена SQL задача парсинга новостей с сайта {base_url} в разделе {categoriesName} c id {task_id}")
        # await send_task_status(task_id, "PROGRESS", f"{now} Запущена задача парсинга новостей с сайта {base_url} в разделе {categoriesName} c id {task_id}")
        # time.sleep(2)

        #старый запроса к сайту с повторными попытками
        #response = requests.get(url, headers=headers, timeout=10)
        #вариант запроса к сайту с повторными попытками
        for _ in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                break
            except RequestException as e:
                print(f"{now} Ошибка при обращении к сайту новостей: {e}")
                time.sleep(5)
        else:
            print(f"{now} Запрос данных с сайта новостей не удался после 3 попыток, проверьте доступность сайта")

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
                # сделать привязку к разным разделам
                "pk": categoriesPk,
                "fields": {
                    # сделать привязку к разным разделам
                    "name": categoriesName,
                    "slug": categoriesSlug
                }
            }
            # data = [categories] if not existing_data else []
            for wrapper in post_wrappers:
                a_tags = wrapper.find_all('a', href=True)
                for a_tag in a_tags:
                    href = a_tag['href']
                    if not href.startswith('/category/') and not href.startswith('/author/'):
                        full_url = base_url + href
                        news_links.append(full_url)

            print(f'{now} получены ссылки для анализа: ' + ', '.join(news_links))
            async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} получены ссылки для анализа: {(news_links)}")
            # time.sleep(2)
            # инициализация счетчика новостей доступных для импорта
            news_count = 0
            # инициализация счетчика дубликатов новостей для лога
            dublicate_count = 0
            for news_link in news_links:

                #старый запроса к сайту с повторными попытками
                #post_response = requests.get(news_link, headers=headers, timeout=10)

                #вариант запроса к сайту с повторными попытками
                for _ in range(3):
                    try:
                        post_response = requests.get(news_link, headers=headers, timeout=10)
                        break
                    except RequestException as e:
                        print(f"{now} Ошибка при обращении к сайту новостей: {e}")
                        time.sleep(5)
                else:
                    print(f"{now} Запрос данных с сайта новостей не удался после 3 попыток, проверьте доступность сайта")

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
                        print(f'{now} Пропуск новости с некорректной датой: {date_str}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'Пропуск новости с некорректной датой: {date_str}')
                        continue  # Пропускаем новость с некорректной датой

                    title = post_soup.find("h1", class_='postContentTitle')
                    if title:
                        title = title.text
                    else:
                        print(f'{now} Пропуск новости без заголовка: {news_link}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'Пропуск новости без заголовка: {news_link}')
                        continue  # Пропускаем новость без заголовка

                    content = post_soup.find("div", class_='articleContent')
                    if content:
                        content = content.text
                    else:
                        print(f'{now} Пропуск новости без содержания: {news_link}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'Пропуск новости без содержания: {news_link}')
                        continue  # Пропускаем новость без содержания

                    author = post_soup.find("div", class_='author_info_text')
                    if author:
                        author = author.text
                    else:
                        print(f'{now} Пропуск новости без автора: {news_link}')
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
                    # переделываем структуру под сохранение напрямую в БД
                    
                    if title not in existing_titles:
                        from news.models import News
                        news_post = News(
                            pk=news_pk,  # Присваиваем новый PK (если это необходимо)
                            title=title,
                            slug=slug,
                            content=content,
                            # time_create=datetime.now(),
                            # time_update=datetime.now(),
                            time_create=aware_date(datetime.now()),
                            time_update=aware_date(datetime.now()),
                            is_published=True,
                            # is_sent=False,
                            cat_id=categoriesPk,  # Привязка к категории
                            date=date,
                            author=author,
                            image=image_url
                        )
                        # Сохранение объекта в базу данных
                        print(f'{now} Сохранение в базу поста: {news_post}')
                        async_to_sync(send_task_status)(task_id, "PROGRESS", f'{now} Сохранение в базу поста: {news_post}')
                        
                        
                        # try:
                        #     news_post.save()
                        # except Exception as e:
                        #     print(f"Ошибка сохранения: {e}")
                        from django.db import transaction
                        with transaction.atomic(using='default', savepoint=True):
                            news_post.save()
                        # data.append(news_post)
                        news_pk += 1
                        news_count += 1
                    else:
                        dublicate_count += 1
                        print(f'{now} Дубликат найден и пропущен: {title}')
                        # async_to_sync(send_task_status)(task_id, "PROGRESS", f'{now} Дубликат найден и пропущен: {title}')
                else:
                    print(f'{now} полученная ссылка: {news_link} не доступна для анализа')
                    async_to_sync(send_task_status)(task_id, "PROGRESS", f'{now} полученная ссылка: {str(news_link)} не доступна для анализа')
                    return False
        else:
            print(f'{now} ссылка сайта: {base_url} не доступна для анализа')
            async_to_sync(send_task_status)(task_id, "PROGRESS", f'ссылка сайта: ' + str(base_url) + ' не доступна для анализа')
            return False
        async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} Запущена SQL задача парсинга новостей с сайта {base_url} в разделе {categoriesName} c id {task_id}")

        async_to_sync(send_task_status)(task_id, "PROGRESS", f'{now} Добавлено {news_count} новостей, обнаружено {dublicate_count} дубликатов новостей которые не были загружены в базу данных')

        print(f'{now} Было добавлено {news_count} новостей')
        print(f'{now} Пропущено {dublicate_count} дубликатов')
        # time.sleep(2)
        # with open(output_path, 'w', encoding='utf-8') as json_file:
        #     json.dump(data, json_file, ensure_ascii=False, indent=2)

        #     async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} в файл: {output_path} сохранено {news_count} постов новостей cisoclub которые можно импортировать")
        #     # time.sleep(2)
        return True

    except Exception as e:
        print(f'{now} получение новостей с сайта cisoclub завершилось с ошибкой: {e}')
        return f'{now} An error occurred: {e}'
            # Обработка мягкого лимита (например, частичное завершение)
    except SoftTimeLimitExceeded:
        print(f"{now} Задача превысила мягкий лимит времени и будет завершена.")
