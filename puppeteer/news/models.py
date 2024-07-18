from django.db import models
from django.urls import reverse

class News(models.Model):
    #через verbose_name задали наименование поля для отображения в админ панеле
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    #добавления использования slug в записях БД
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name='Статья')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    #внешний ключ для связи с первичной моделью Category как cat_id (id добавляется атоматом)
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    #новые поля
    date = models.DateField(verbose_name='Дата статьи')
    author = models.CharField(max_length=255, blank=True, null=True, verbose_name='Автор')
    #image = models.ImageField(upload_to='news_image', blank=True, null=True, verbose_name='Изображение')
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name='Изображение')
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})
    #Класс для админ панели и поменяет отображение там на установленное
    class Meta:
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'
        #сортировка по времени создания и заголовку, она применится и на основной части сайта
        ordering = ['id', 'time_create', 'title']

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