# Generated by Django 4.2.6 on 2024-10-13 23:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0014_alter_telegramsubscriber_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=100, verbose_name='Название города')),
                ('city_latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Широта')),
                ('city_longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Долгота')),
                ('city_created_at', models.DateTimeField(auto_now_add=True)),
                ('city_updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
                'ordering': ['city_name'],
            },
        ),
        migrations.AlterField(
            model_name='telegramsubscriber',
            name='subscribed_weather_city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='news.city', verbose_name='Подписка на прогноз погоды по городу'),
        ),
    ]
