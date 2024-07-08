from django import template
from news.models import *

register = template.Library()
#превращаем функцию в тег с помощью декоратора
@register.simple_tag(name='getcats')
#функция для работы простого тега, производится выборка всех категорий из модели Category
def get_categories():
    return Category.objects.all()

#формируем щаблон html который вернется включающим тегом
@register.inclusion_tag('news/list_categories.html')
def show_categories(sort=None, cat_selected=0):
    if not sort:
        cats = Category.objects.all()
    else:
        cats = Category.objects.order_by(sort)

    return {"cats": cats, 'cat_selected': cat_selected}

@register.inclusion_tag('women/tag_menu.html')
def tag_menu():
    menu = [{"title": "О сайте", "url_name": "about"},
            {"title": "Добавить статью", "url_name": "add_page"},
            {"title": "Обратная связь", "url_name": "contact"},
            {"title": "Войти", "url_name": "login"}
            ]
    return {"menu": menu}