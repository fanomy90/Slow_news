# Generated by Django 4.2.6 on 2024-07-19 14:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_alter_category_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['id'], 'verbose_name': 'Категория', 'verbose_name_plural': 'Категория'},
        ),
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-id', 'time_create', 'title'], 'verbose_name': 'Новости', 'verbose_name_plural': 'Новости'},
        ),
    ]
