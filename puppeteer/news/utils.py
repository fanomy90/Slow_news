from django.db.models import Count
from .models import *

menu = [{"title": "Домой", "url_name": "home"},
        {"title": "Добавить статью", "url_name": "add_page"},
        {"title": "О Сайте", "url_name": "about"},
        ]

class DataMixin:
    #использование многостраничности для вывода контента
    paginate_by = 10
    #создание контекста для шаблона
    def get_user_context(self, **kwargs):
        # формируем начальный словарь из именованных параметров kwargs переданных функции
        context = kwargs
        # формируем список категорий, через Count добавили свойство с количеством статей в категории
        cats = Category.objects.annotate(Count('news'))
    #видимость раздела меню для авторизаванного пользователя
        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            #удаляем второй элемент Добавить статью для неавторизованного пользователя
            user_menu.pop(1)
        context['menu'] = user_menu
        context['cats'] = cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context