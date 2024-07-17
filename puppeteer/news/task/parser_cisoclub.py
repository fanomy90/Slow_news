import os
import uuid #для генерации случайных имен файлов
from django.utils.timezone import now
import json
import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils.text import slugify
import requests
from bs4 import BeautifulSoup
from django.core.management import call_command


url = 'https://cisoclub.ru/category/news/'
now = datetime.datetime.now()
output_dir = '/app/puppeteer/SAVE'
output_path = os.path.join(output_dir, 'news.json')
output_path_history = os.path.join(output_dir, 'news_history.json')
#загрузим старый файл для анализа
# def load_existing_data(file_path):
#     if os.path.exists(file_path):
#         with open(file_path, 'r', encoding='utf-8') as json_file:
#             return json.load(json_file)
#     return []
#загрузим старые данные из бд для анализа
def load_existing_data(file_path):
    print(str(now) + ' получим исторические данные')
    try:
        call_command('dumpdata', 'news', indent=2, output=file_path)
        print(str(now) + ' получены исторически данные: ' + file_path)
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(str(now()) + ' получение исторических данных завершилось с ошибкой: ' + str(e))
        return []
#получим максимальный pk постов из старого файла
def get_max_pk(data):
    max_pk = 0
    for item in data:
        if 'pk' in item and isinstance(item['pk'], int) and item['pk'] > max_pk:
            max_pk = item['pk']
    return max_pk
#получим заголовки новостей из старого файла
def get_existing_titles(data):
    titles = set()
    for item in data:
        if item['model'] == 'news.news' and 'fields' in item and 'title' in item['fields']:
            titles.add(item['fields']['title'])
    return titles
#основной скрипт парсера
def cisoclub_news():
    # now = datetime.datetime.now()
    if not os.path.exists(output_dir):
        #os.makedirs(output_dir)
        print(str(now) + ' не найдена директория для сохранения: ' + output_dir)
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125'
        }

        #анализ старого файла
        # if not os.path.exists(output_path_history):
        #     print(str(now) + ' не найдена файл с историческими данными: ' + output_path_history)
        #     try:
        #         # Запускаем команду dumpdata
        #         call_command('dumpdata', 'news', indent=2, output=output_path_history)
        #         print(str(now) + ' получены исторически данные: ' + output_path_history)
        #     except Exception as e:
        #         print(str(now()) + ' получение исторических данных завершилось с ошибкой: ' + str(e))

        #если файл есть то добавить логику сравнения файла с базой
        #как вариант в будущем делать запросы к бд а не выгружать каждый раз файл
        existing_data = load_existing_data(output_path_history)
        max_existing_pk = get_max_pk(existing_data)
        existing_titles = get_existing_titles(existing_data)
        #статические данные парсера
        href = []
        cat_id = 1
        category_name = "Безопасность"
        category_slug = "security"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            src = response.text
            soup = BeautifulSoup(src, 'lxml')
            post_wrappers = soup.find_all("div", class_='postWrapper')
            news_links = []
            news_data = []
            base_url = 'https://cisoclub.ru'
            #делаем начальное значение pk постов в новом наборе учитывая максимальный pk из старого файла
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
                    #else:
                    #    print('в блоке: ' + str(wrapper) + 'нет ссылки для анализа')
            print('получены ссылки для анализа: ' + ', '.join(news_links))
            for news_link in news_links:
                post_response = requests.get(news_link, headers=headers)
                if post_response.status_code == 200:
                    post_src = post_response.text
                    post_soup = BeautifulSoup(post_src, 'lxml')
                    date = post_soup.find("div", class_='postDate').text
                    title = post_soup.find("h1", class_='postContentTitle').text
                    content = post_soup.find("div", class_='articleContent').text
                    author = post_soup.find("div", class_='author_info_text').text
                    image = post_soup.find("div", class_='imageWrapper')
                    image2 = image.find('img', src=True)
                    image3 = image2['src']
                    image_url = base_url + image3
                    slug = news_link.replace('https://', '').replace('/', '').replace('.', '-')
                    if title not in existing_titles:
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
                        #existing_titles.add(title)  # Добавляем заголовок в набор существующих заголовков
                    else:
                        print(f'Дубликат найден и пропущен: {title}')
                else:
                    print('полученная ссылка: ' + str(news_link) + ' не доступна для анализа')
                    return False
                # создаем полный набор постов из старого и нового набора
                #combined_data = existing_data + data
        else:
            print('ссылка сайта: ' + str(base_url) + ' не доступна для анализа')
            return False
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
            print(str(now) + ' посты новостей cisoclub сохранены в файл: ' + str(output_path))
        # with open(output_path_history, 'w', encoding='utf-8') as json_file:
        #     json.dump(combined_data, json_file, ensure_ascii=False, indent=2)
        #     # print(f'{datetime.datetime.now()} посты новостей cisoclub сохранены в файл {output_path}')
        #     print(str(now) + ' дополнен файл постов новостей cisoclub: ' + str(output_path_history))
        return True
    except Exception as e:
        print(str(now) + ' получение новостей с сайта cisoclub завершилось с ошибкой: ' + str(e))
        return f'An error occurred: {e}'