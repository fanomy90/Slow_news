from django.contrib import admin
from .models import *
#вспомогательный класс для админ панели
class NewsAdmin(admin.ModelAdmin):
    #вывод дополнительных полей для отображения записей БД в админке
    list_display = ('id', 'slug', 'title', 'time_create', 'is_published')
    #Доп поля с ссылками для перехода для редактирования записи БД
    list_display_links = ('id', 'title')
    #Доп поля по которым можно произвести поиск
    search_fields = ('title', 'content')
    #Разрешение редактирования параметра публикации в админке
    list_editable = ('is_published',)
    #Возможность фильтрации записей в админке по публикации и дате создания
    list_filter = ('is_published', 'time_create')
    #Автоматическое создание слага по введенному полю в админке
    prepopulated_fields = {"slug": ("title",)}

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'name')
    list_display_links = ('id', 'name')
    #так как передаем кортеж то для одного элемента надо поставить запятую
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(News, NewsAdmin)
admin.site.register(Category, CategoryAdmin)