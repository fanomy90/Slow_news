from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView
# from . import tasks
from celery.result import AsyncResult
from rest_framework.views import APIView
# from news.tasks import cpu_task1, cpu_task2
from django.shortcuts import render

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from news.utils import DataMixin
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, FormView
from .utils import menu  # Импортируйте menu
class NewsHome(DataMixin, ListView):
    model = News
    template_name = 'news/index.html'
    context_object_name = 'posts'
    extra_context = {'title': 'Главная страница'}
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #показываем карусель
        show_slider_header = True
        c_def = self.get_user_context(title='Главная страница',
                                    show_slider_header=show_slider_header) #добавил кусок после title
        return dict(list(context.items())+list(c_def.items()))
    def get_queryset(self):
        return News.objects.filter(is_published=True)

class AboutFormView(DataMixin, FormView):
    model = News
    form_class = ContactForm
    template_name = 'news/about.html'
    success_url = reverse_lazy('home')
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #скрываем карусель
        show_slider_header = False
        #добавляем установку активного пункта меню
        active_menu_item = next((item for item in menu if item['url_name'] == 'about'), None)
        c_def = self.get_user_context(
                title="О сайте",
                cat_selected=active_menu_item,
                show_slider_header=show_slider_header) #добавил кусок после title
        return dict(list(context.items()) + list(c_def.items()))

class Register(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'news/register.html'
    success_url = reverse_lazy('login')
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #скрываем карусель
        show_slider_header = False
        c_def = self.get_user_context(title='Регистрация',
                                    show_slider_header=show_slider_header) #добавил кусок после title
        return dict(list(context.items())+list(c_def.items()))
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class Login(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'news/login.html'
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #скрываем карусель
        show_slider_header = False
        c_def = self.get_user_context(title="Авторизация",
                show_slider_header=show_slider_header) #добавил кусок после title
        return dict(list(context.items())+list(c_def.items()))
    def get_success_url(self):
        return reverse_lazy('home')

class AddPage(DataMixin, ListView):
    paginate_by = None  # Отключаем пагинацию
    model = News
    template_name = 'news/import_news_template.html'
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #скрываем карусель
        show_slider_header = False
        #добавляем установку активного пункта меню
        active_menu_item = next((item for item in menu if item['url_name'] == 'add_page'), None)
        c_def = self.get_user_context(
                title="Добавление новостей",
                cat_selected=active_menu_item,
                show_slider_header=show_slider_header) #добавил кусок после title
        return dict(list(context.items()) + list(c_def.items()))

class NewsCategory(DataMixin, ListView):
    model = News
    template_name = 'news/index.html'
    context_object_name = 'posts'
    # вывод ошибки 404 при обращении к несуществующей статьи
    def get_queryset(self):
        return News.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True)
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #показываем карусель
        show_slider_header = True
        # вызываем метод из базового класса DataMixin файла utils
        cat_selected = context['posts'][0].cat  # Присваиваем объект категории
        c_def = self.get_user_context(
            title='Категория - '+str(context['posts'][0].cat),
            cat_selected=cat_selected,
            show_slider_header=show_slider_header) #добавил кусок после cat_selected
        return dict(list(context.items())+list(c_def.items()))

class ShowPost(DataMixin, DetailView):
    model = News
    template_name = 'news/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #скрываем карусель
        show_slider_header = False
        # Получаем объект новости, для которой пытаемся получить категорию
        post = self.get_object()
        # Теперь, используя объект новости, получаем связанную с ней категорию
        cat_selected = post.cat
        c_def = self.get_user_context(
                title=context['post'],
                cat_selected=cat_selected, # Преобразуем cat_selected в целое число
                show_slider_header=show_slider_header) 
        return dict(list(context.items()) + list(c_def.items()))

def Logout(request):
    logout(request)
    return redirect('login')

# домашняя страница - заглушка
# def home(request):
#     tasks.download_a_cat.delay()
#     return HttpResponse('<g1>Гружу кота</h1>')
# запуск задачи
class TaskSetter(APIView):
    def get(self, request, formant=None):
        res = tasks.download_a_cat.delay()
        return Response(res.id)
# отслеживание состояния задачи
class TaskGetter(APIView):
    def get(self, request, formant=None):
        task_id = request.GET.get('task_id')
        if task_id:
            res = AsyncResult(task_id)
            return Response(res_state)
        return Response('no id pas provided')
# страница запуска задачи
def AddTask(request):
    return render(request, "news/task_tracker.html")