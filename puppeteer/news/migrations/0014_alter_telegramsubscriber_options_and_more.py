# Generated by Django 4.2.6 on 2024-10-12 23:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0013_currency_telegramsubscriber_frequency_sending_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='telegramsubscriber',
            options={'ordering': ['subscribed_at'], 'verbose_name': 'Подписчик Telegram', 'verbose_name_plural': 'Подписчики Telegram'},
        ),
        migrations.RemoveField(
            model_name='currency',
            name='currency_date',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='currency_rate',
        ),
        migrations.AddField(
            model_name='currency',
            name='symbol',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Символ валюты'),
        ),
        migrations.CreateModel(
            name='CurrencyRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата курса')),
                ('rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Курс валюты')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='news.currency', verbose_name='Валюта')),
            ],
            options={
                'verbose_name': 'Курс валюты',
                'verbose_name_plural': 'Курсы валют',
                'ordering': ['-date'],
                'unique_together': {('currency', 'date')},
            },
        ),
    ]
