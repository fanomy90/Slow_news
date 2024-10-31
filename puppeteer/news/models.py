from django.db import models
from django.urls import reverse

class News(models.Model):
    #через verbose_name задали наименование поля для отображения в админ панеле
    title = models.CharField(max_length=455, verbose_name='Заголовок')
    #добавления использования slug в записях БД
    slug = models.SlugField(max_length=455, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name='Статья')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    is_sent = models.BooleanField(default=False, verbose_name='В соцсети')  # Новое поле для отслеживания отправки новостей
    #внешний ключ для связи с первичной моделью Category как cat_id (id добавляется атоматом)
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    #новые поля
    date = models.DateField(verbose_name='Дата статьи')
    author = models.CharField(blank=True, null=True, verbose_name='Автор')
    #image = models.ImageField(upload_to='news_image', blank=True, null=True, verbose_name='Изображение')
    image = models.CharField(blank=True, null=True, verbose_name='Изображение')
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})
    #Класс для админ панели и поменяет отображение там на установленное
    class Meta:
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'
        #сортировка по времени создания и заголовку, она применится и на основной части сайта
        ordering = ['-date', 'id', 'time_create', 'title']

#сделаем нормализацию - привяжем вторичную модель по категориям
class Category(models.Model):
    #название категории связанной таблицы с инексацией для ускорения поиска
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    #метод для возврата имя категории
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})
    #Для вывода в админ панели
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категория'
        ordering = ['id']

class Currency(models.Model):
    # currency_name = models.CharField(max_length=255, unique=True, verbose_name='Название валюты')
    currency_name = models.CharField(max_length=255, verbose_name='Название валюты')
    symbol = models.CharField(max_length=10, unique=True, verbose_name='Символ валюты', blank=True, null=True)
    def __str__(self):
        return f'{self.currency_name} ({self.symbol})'

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'
        ordering = ['currency_name']

class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates', verbose_name='Валюта')
    date = models.DateField(verbose_name='Дата курса')  # Дата, за которую указан курс
    rate = models.DecimalField(max_digits=20, decimal_places=4, verbose_name='Курс валюты')

    @property
    def symbol(self):
        return self.currency.symbol

    def __str__(self):
        return f'{self.currency} - {self.rate} (на {self.date})'

    class Meta:
        verbose_name = 'Курс валюты'
        verbose_name_plural = 'Курсы валют'
        ordering = ['-date']  # Сортировка по дате (от новых к старым)
        unique_together = ['currency', 'date']  # Уникальность записи на определенную дату для конкретной валюты
class City(models.Model):
    city_name = models.CharField(max_length=100, verbose_name="Название города")
    city_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Широта")
    city_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Долгота")
    city_created_at = models.DateTimeField(auto_now_add=True)
    city_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city_name
    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ['city_name']

#пользователи телеграм
class TelegramSubscriber(models.Model):
    #данные пользователя
    chat_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    #настройки подписки
    news_sent = models.BooleanField(default=False, verbose_name='Подписка на новости')
    subscribed_to_categories = models.ManyToManyField('Category', blank=True, verbose_name='Категориии новостей')
    currency_sent = models.BooleanField(default=False, verbose_name='Подписка на валюты')
    subscribed_to_currency = models.ManyToManyField('Currency', blank=True, verbose_name='Валюты для курсов')
    weather_sent = models.BooleanField(default=False, verbose_name='Подписка на прогноз погоды')
    #subscribed_weather_city = models.ForeignKey ('City', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Города для прогноза')
    subscribed_weather_city = models.ManyToManyField('City', blank=True, verbose_name='Города для прогноза')
    # Настройки формата сообщений (полные или сокращенные)
    MESSAGE_FORMAT_CHOICES = [
        ('full', 'Полные сообщения'),
        ('short', 'Сокращенные сообщения'),
    ]
    message_format = models.CharField(
        choices=MESSAGE_FORMAT_CHOICES,
        default='short',
        verbose_name='Формат сообщений'
    )
    # Периодичность рассылки
    FREQUENCY_CHOICES = [
        ('every_hour', 'Каждый час'),
        ('every_3hour', 'Каждые 3 часа'),
        ('every_6hour', 'Каждые 6 часов'),
        ('every_9hour', 'Каждые 9 часов'),
        ('every_12hour', 'Каждые 12 часов'),
        ('daily', 'Ежедневно'),
    ]
    frequency_sending = models.CharField(
        choices=FREQUENCY_CHOICES,
        default='every_hour',
        verbose_name='Частота рассылки'
    )

    def __str__(self):
        return f'{self.username} ({self.chat_id})'

    class Meta:
        verbose_name = 'Подписчик Telegram'
        verbose_name_plural = 'Подписчики Telegram'
        ordering = ['subscribed_at']