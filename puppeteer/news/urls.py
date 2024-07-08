from django.urls import path, re_path
from . import views
from .views import *

urlpatterns = [
    # path('', views.home, name='home'),
    path('', NewsHome.as_view(), name='home'),
    path('logout/', Logout, name='logout'),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', NewsCategory.as_view(), name='category'),
    # path('about/', views.about, name='about'),
    # path('addpage/', views.addpage, name='addpage'),
    # path('contact/', views.contact, name='contact'),
    # path('login/', views.login, name='login'),

    path('about/', AboutFormView.as_view(), name='about'),
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('addpage/', AddPage.as_view(), name='add_page'),

    path('settask/', views.TaskSetter.as_view(), name='settask'),
    path('gettask/', views.TaskGetter.as_view(), name='gettask'),
    path('addtask/', views.AddTask, name="addTask"),
    # path('showpost/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    # path('category/<slug:cat_slug>/', NewsCategory.as_view(), name='category'),
    # path('post/<int:post_id>/', views.show_post, name='post'),
]