# Generated by Django 4.2.6 on 2024-10-30 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0019_alter_currency_currency_name_alter_currency_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyrate',
            name='rate',
            field=models.DecimalField(decimal_places=4, max_digits=20, verbose_name='Курс валюты'),
        ),
    ]