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

#костыль для обрезания вывода описания автора в каталоге статей
@register.filter
def trim_author(text):
    if text:
        # Ищем индекс первого вхождения двух пробелов
        index = text.find('  ')
        if index != -1:
            return text[:index]
    return text

#костыль для для установки цвета шапки статьи в зависимости от категории
@register.simple_tag
def tag_color(cat):
    cat_str = str(cat)
    colors = {
        'Безопасность': 'green',
        'Обзоры': 'purple',
        'Статьи': 'red'
    }
    color = colors.get(cat_str, '#333671')  # Цвет по умолчанию
    return f'background: {color};'