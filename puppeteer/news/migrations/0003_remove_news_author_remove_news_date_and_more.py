# Generated by Django 4.2.6 on 2024-07-18 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_news_author_news_date_news_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='author',
        ),
        migrations.RemoveField(
            model_name='news',
            name='date',
        ),
        migrations.RemoveField(
            model_name='news',
            name='image',
        ),
    ]
