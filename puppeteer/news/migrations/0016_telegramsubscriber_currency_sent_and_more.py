# Generated by Django 4.2.6 on 2024-10-14 00:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0015_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramsubscriber',
            name='currency_sent',
            field=models.BooleanField(default=False, verbose_name='Подписка на валюты'),
        ),
        migrations.AddField(
            model_name='telegramsubscriber',
            name='news_sent',
            field=models.BooleanField(default=False, verbose_name='Подписка на новости'),
        ),
        migrations.AddField(
            model_name='telegramsubscriber',
            name='weather_sent',
            field=models.BooleanField(default=False, verbose_name='Подписка на прогноз погоды'),
        ),
        migrations.AlterField(
            model_name='telegramsubscriber',
            name='subscribed_to_currency',
            field=models.ManyToManyField(blank=True, to='news.currency', verbose_name='Валюты для курсов'),
        ),
        migrations.AlterField(
            model_name='telegramsubscriber',
            name='subscribed_weather_city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='news.city', verbose_name='Города для прогноза'),
        ),
    ]
