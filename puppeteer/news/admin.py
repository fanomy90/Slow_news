from django.contrib import admin
from django import forms
from .models import *
import json
# Загрузка списка городов
# def get_city_choices():
#     #выбираем файл с городами для загрузки
#     with open('news/cities.json', 'r', encoding='utf-8') as f:
#         cities = json.load(f)
#         #конвертируем города в формат choices
#         return [(city['city'], city['city']) for city in cities]
# # Загрузка списка валют
# def get_currency_choices():
#     #выбираем файл с городами для загрузки
#     with open('news/currencies.json', 'r', encoding='utf-8') as f:
#         currencies = json.load(f)
#         #конвертируем города в формат choices
#         return [(currency['currency'], currency['currency']) for currency in currencies]
# Форма для TelegramSubscriberAdmin
class TelegramSubscriberForm(forms.ModelForm):
    class Meta:
        model = TelegramSubscriber
        fields = '__all__'

    #subscribed_weather_city = forms.ChoiceField(choices=get_city_choices(), required=False, label='Город для прогноза погоды')
    #subscribed_currency = forms.ChoiceField(choices=get_currency_choices(), required=False, label='Курсы валют')
#вспомогательный класс для админ панели
class NewsAdmin(admin.ModelAdmin):
    #вывод дополнительных полей для отображения записей БД в админке
    list_display = ('id', 'slug', 'title', 'get_category_name', 'time_create', 'is_published', 'is_sent', 'date')
    #Доп поля с ссылками для перехода для редактирования записи БД
    list_display_links = ('id', 'title')
    #Доп поля по которым можно произвести поиск
    search_fields = ('title', 'cat__name', 'content')
    #Разрешение редактирования параметра публикации в админке
    list_editable = ('is_published', 'is_sent')
    #Возможность фильтрации записей в админке по публикации и дате создания
    list_filter = ('cat', 'is_published', 'is_sent', 'time_create')
    #Автоматическое создание слага по введенному полю в админке
    prepopulated_fields = {"slug": ("title",)}

    def get_category_name(self, obj):
        return obj.cat.name  # Возвращаем имя категории
    get_category_name.short_description = 'Категория'  # Задаем название столбца в админке

class NewsSentAdmin(admin.ModelAdmin):
    #вывод дополнительных полей для отображения записей БД в админке
    list_display = ('id', 'subscriber', 'news', 'sent_at')
    #Доп поля с ссылками для перехода для редактирования записи БД
    list_display_links = ('id', 'subscriber', 'news')
    #Доп поля по которым можно произвести поиск
    search_fields = ('subscriber__username', 'news__title', 'sent_at')
    #Возможность фильтрации записей в админке по публикации и дате создания
    list_filter = ('subscriber', 'news', 'sent_at')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'name')
    list_display_links = ('id', 'name')
    #так как передаем кортеж то для одного элемента надо поставить запятую
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

class CurrencyRateInline(admin.TabularInline):
    model = CurrencyRate
    extra = 1  # Количество пустых форм для добавления новых записей
    fields = ('date', 'rate')
    readonly_fields = ('date', 'rate')  # Только для чтения, если не хочешь редактировать здесь

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'currency_name', 'symbol')
    list_display_links = ('id', 'currency_name')
    search_fields = ('currency_name', 'symbol')
    inlines = [CurrencyRateInline]  # Включаем в админку курсы валют для каждой валюты

class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'date', 'rate')
    list_display_links = ('currency',)
    search_fields = ('currency__currency_name', 'date', 'rate')  # Поиск по имени валюты и дате
    list_filter = ('currency', 'date')  # Фильтр по валюте и дате
    ordering = ['-date', 'currency']  # Сортировка по дате и валюте

class CityAdmin(admin.ModelAdmin):
    #вывод дополнительных полей для отображения записей БД в админке
    list_display = ('id', 'city_name', 'city_created_at', 'city_updated_at', 'city_latitude', 'city_longitude')
    #Доп поля с ссылками для перехода для редактирования записи БД
    list_display_links = ('id',)
    #Доп поля по которым можно произвести поиск
    search_fields = ('city_name', 'city_latitude', 'city_longitude')
    #Разрешение редактирования параметра публикации в админке
    list_editable = ('city_name', 'city_latitude', 'city_longitude')
    #Возможность фильтрации записей в админке по публикации и дате создания
    list_filter = ('city_name', 'city_latitude', 'city_longitude')
    readonly_fields = ('city_created_at', 'city_updated_at')

class TelegramSubscriberAdmin(admin.ModelAdmin):
    #вызов кастомной форме для админки для динамической загрузки внещних файлов
    form = TelegramSubscriberForm
    list_display = ('chat_id', 'username', 'subscribed_at','news_sent', 'get_subscribed_categories', 'weather_sent', 'get_subscribed_cities', 'currency_sent', 'get_subscribed_currencies', 'frequency_sending', 'message_format')
    list_display_links = ('chat_id', 'username')
    #так как передаем кортеж то для одного элемента надо поставить запятую
    search_fields = ('username',)
    list_editable = ('news_sent', 'currency_sent', 'weather_sent', 'frequency_sending', 'message_format')
    # Добавляем удобный виджет для редактирования ManyToMany поля
    filter_horizontal = ('subscribed_to_categories', 'subscribed_weather_city', 'subscribed_to_currency')  # Или filter_vertical

    # Метод для отображения категорий в списке
    def get_subscribed_categories(self, obj):
        return ", ".join([cat.name for cat in obj.subscribed_to_categories.all()])
    get_subscribed_categories.short_description = 'Категории новостей'

    # Метод для отображения городов
    def get_subscribed_cities(self, obj):
        return ", ".join([city.city_name for city in obj.subscribed_weather_city.all()])
    get_subscribed_cities.short_description = 'Города для прогноза'

    # Отображение валют для подписки
    def get_subscribed_currencies(self, obj):
        return ", ".join([cur.currency_name for cur in obj.subscribed_to_currency.all()])
    get_subscribed_currencies.short_description = 'Валюты для курсов'

    # # Поле для выбора города на основе загруженного файла
    # subscribed_weather_city = models.CharField(
    #     max_length=255,
    #     choices=get_city_choices(),
    #     blank=True,
    #     verbose_name='Город для прогноза погоды'
    # )
    # # Поле для выбора валют на основе загруженного файла
    # subscribed_currency = models.CharField(
    #     max_length=255,
    #     choices=get_currency_choices(),
    #     blank=True,
    #     verbose_name='Курсы валют'
    # )



admin.site.register(News, NewsAdmin)
admin.site.register(NewsSent, NewsSentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TelegramSubscriber, TelegramSubscriberAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(CurrencyRate, CurrencyRateAdmin)
admin.site.register(City, CityAdmin)