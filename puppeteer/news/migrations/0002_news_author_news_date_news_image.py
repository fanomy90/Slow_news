# Generated by Django 4.2.6 on 2024-07-18 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
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
        migrations.AddField(
            model_name='news',
            name='image',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Изображение'),
        ),
    ]
