import os

import uuid #для генерации случайных имен файлов
#from django.core.management import call_command
from django.utils.timezone import now
import json
import datetime

from django.conf import settings

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
# from news.models import News, Category
from django.utils.text import slugify

import requests
#import requests as r # для закачки файлов
from bs4 import BeautifulSoup

now = datetime.datetime.now()
#сайт для получения данных
url = 'https://cisoclub.ru/category/news/'

#пути для сохранения файлов парсинга в контейнере проекта
#output_dir = '/app/puppeteer/SAVE'
output_dir = '/home/projects/SAVE'
output_path = os.path.join(output_dir, 'news.json')

#пути для сохранения файлов парсинга для отладки на сервере разработки
# output_dir = '/home/projects/SAVE'
# output_path = os.path.join(output_dir, 'test_page.html')

#имитация работы браузера для обхода блокировок
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers)

#обработка сохранения страцницы для анализа
if response.status_code == 200:
    src = response.text
    # with open(output_path, "w", encoding='utf-8') as file:
    #     file.write(src)
    # print("тестовая страницы успешно сохранена в" + output_dir)
    #print(src)
    soup = BeautifulSoup(src, 'lxml')
    post_wrappers = soup.find_all("div", class_='postWrapper')
    news_links = []
    #news_posts = []
    news_data = []
    base_url = 'https://cisoclub.ru'  # Базовый URL для ссылок
    cat_id = 1
    news_pk = 1  # Начальное значение pk
    category_name = "Безопасность"
    category_slug = "security"
    #print(post_wrappers)
    #str_post = str(post_wrappers)
    #with open(output_path, "w", encoding='utf-8') as file:
    #    file.write(str_post)

    #собираем структуру каталогов статей в json файле
    categories = {
        "model": "news.category",
        "pk": 1,
        "fields": {
            "name": "Безопасность",
            "slug": "security"
        }
    }

    data = [categories]
    
    for wrapper in post_wrappers:
        a_tags = wrapper.find_all('a', href=True)  # Находим первый тег 'a' с атрибутом 'href'
        for a_tag in a_tags:
            href = a_tag['href']
            # Проверяем, что ссылка ведет на конкретную новость
            if not href.startswith('/category/') and not href.startswith('/author/'):
                full_url = base_url + href  # Добавляем базовый URL к относительной ссылке
                news_links.append(full_url)

    for news_link in news_links:
        post_response = requests.get(news_link, headers=headers)
        if post_response.status_code == 200:
            post_src = post_response.text
            post_soup = BeautifulSoup(post_src, 'lxml')
            #разбираем сохраненную страницу
            #продумать использовании даты статьи в моделях и фильтрах
            date = post_soup.find("div", class_='postDate').text
            title = post_soup.find("h1", class_='postContentTitle').text
            content = post_soup.find("div", class_='articleContent').text
            author = post_soup.find("div", class_='author_info_text').text
            #ссылка на картинку - надо доработать и сделать вариант с сохранением картинки
            image = post_soup.find("div", class_='imageWrapper')
            image2 = image.find('img', src=True)
            image3 = image2['src']
            image_url = base_url + image3
            #slug = slugify(title)
            slug = news_link.replace('https://', '').replace('/', '').replace('.', '-')
            #собираем структуру статей в json файле
            # news_post = {
            #     "title": title,
            #     "slug": slug,
            #     "content": content,
            #     "photo": image_url,
            #     "cat": cat_id
            # }
            # news_data.append(news_post)
            news_post = {
                "model": "news.news",
                "pk": news_pk,
                "fields": {
                    "title": title,
                    "slug": slug,
                    "content": content,
                    "time_create": datetime.datetime.now().isoformat(),
                    "time_update": datetime.datetime.now().isoformat(),
                    "is_published": True,
                    "cat": 1
                }
            }
            data.append(news_post)
            news_pk += 1

    #собираем окончательную структуру json файла
    #data = [news_data, categories]
    #сохраняем данные в файл
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        #print(str(now) + ' посты новостей cisoclub сохранены в файл' + str(output_path))
        print(f'{datetime.datetime.now()} посты новостей cisoclub сохранены в файл {output_path}')






    #проверяем ссылку и настраиваем скрапинг на примере - переделать для получения данных по всем ссылкам из каталога
#     test_link = 'https://cisoclub.ru/kompanija-vebmonitorjeks-rasskazala-o-roste-atak-na-api-i-predstavila-novuju-partnerskuju-programmu/'
#     test_response = requests.get(test_link, headers=headers)
#     test_post = []
#     if test_response.status_code == 200:
#         test_src = test_response.text
#         #print(test_src)
#         soup2 = BeautifulSoup(test_src, 'lxml')
#         date = soup2.find("div", class_='postDate').text
#         print(date)
#         title = soup2.find("h1", class_='postContentTitle').text
#         print(title)
#         content = soup2.find("div", class_='articleContent').text
#         print(content)
#         author = soup2.find("div", class_='author_info_text').text
#         print(author)
#         image = soup2.find("div", class_='imageWrapper')
#         image2 = image.find('img', src=True)
#         image3 = image2['src']
#         image_url = base_url + image3
#         print(image_url)
#     else:
#         print(f"Ошибка получения тестовой страницы. Status code: {response.status_code}")
# else:
#     print(f"Ошибка получения страницы каталога. Status code: {response.status_code}")



