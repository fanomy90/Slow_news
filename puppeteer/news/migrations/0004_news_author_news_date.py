# Generated by Django 4.2.6 on 2024-07-18 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_remove_news_author_remove_news_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='author',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='news',
            name='date',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата статьи'),
        ),
    ]
