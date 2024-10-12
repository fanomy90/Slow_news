from django.contrib import admin
from .models import *
# Загрузка списка городов
def get_city_choices():
    #выбираем файл с городами для загрузки
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)
        #конвертируем города в формат choices
        return [(city['city'], city['city']) for city in cities]
# Загрузка списка валют
def get_currency_choices():
    #выбираем файл с городами для загрузки
    with open('currencies.json', 'r', encoding='utf-8') as f:
        currencies = json.load(f)
        #конвертируем города в формат choices
        return [(currency['currency'], currency['currency']) for currency in currencies]
# Форма для TelegramSubscriberAdmin
class TelegramSubscriberForm(forms.ModelForm):
    class Meta:
        model = TelegramSubscriber
        fields = '__all__'

    subscribed_weather_city = forms.ChoiceField(choices=get_city_choices(), required=False, label='Город для прогноза погоды')
    subscribed_currency = forms.ChoiceField(choices=get_currency_choices(), required=False, label='Курсы валют')
#вспомогательный класс для админ панели
class NewsAdmin(admin.ModelAdmin):
    #вывод дополнительных полей для отображения записей БД в админке
    list_display = ('id', 'slug', 'title', 'time_create', 'is_published', 'is_sent', 'date', 'author', 'image')
    #Доп поля с ссылками для перехода для редактирования записи БД
    list_display_links = ('id', 'title')
    #Доп поля по которым можно произвести поиск
    search_fields = ('title', 'content')
    #Разрешение редактирования параметра публикации в админке
    list_editable = ('is_published', 'is_sent')
    #Возможность фильтрации записей в админке по публикации и дате создания
    list_filter = ('is_published', 'is_sent', 'time_create')
    #Автоматическое создание слага по введенному полю в админке
    prepopulated_fields = {"slug": ("title",)}

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'name')
    list_display_links = ('id', 'name')
    #так как передаем кортеж то для одного элемента надо поставить запятую
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

class TelegramSubscriberAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'subscribed_at', 'subscribed_to_categories', 'frequency_sending', 'message_format')
    list_display_links = ('chat_id', 'username')
    #так как передаем кортеж то для одного элемента надо поставить запятую
    search_fields = ('username',)
    list_editable = ('subscribed_to_categories', 'frequency_sending', 'message_format')

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
    #вызов кастомной форме для админки для динамической загрузки внещних файлов
    form = TelegramSubscriberForm


admin.site.register(News, NewsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TelegramSubscriber, TelegramSubscriberAdmin)