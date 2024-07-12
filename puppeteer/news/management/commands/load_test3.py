import json
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils.text import slugify
from news  .models import News, Category
import datetime
#файл был подготовлен для тестового сайта про женщин, надо избавиться от этих баб (women_data)
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open('/app/news/SAVE/news.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            categories_data = data['categories']
            women_data = data['news']
            #news_data = data['news']

            for category_data in categories_data:
                name = category_data['name']
                slug = category_data['slug']
                try:
                    category = Category.objects.get(slug=slug)
                except ObjectDoesNotExist:
                    category = Category.objects.create(name=name, slug=slug)

            #for news_data in women_data:
            for news_data in women_data:
                title = news_data['title']
                slug = news_data['slug']
                content = news_data['content']
                #photo_path = news_data['photo']
                cat_id = news_data['cat_id']

                try:
                    category = Category.objects.get(id=cat_id)
                except ObjectDoesNotExist:
                    continue

                try:
                    news = News.objects.get(slug=slug)
                except ObjectDoesNotExist:
                    news = News()

                news.title = title
                news.slug = slug
                news.content = content
                news.cat = category

                #with open(photo_path, 'rb') as photo_file:
                #    news.photo.save(photo_path, File(photo_file), save=True)

                news.save()
                now = datetime.datetime.now()
                print(str(now) + ' import cisoclub in management complete')
            self.stdout.write(self.style.SUCCESS('Successfully loaded test data.'))