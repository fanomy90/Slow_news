# Generated by Django 4.2.6 on 2024-07-18 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_alter_news_author_alter_news_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='date',
            field=models.DateField(verbose_name='Дата статьи'),
        ),
    ]