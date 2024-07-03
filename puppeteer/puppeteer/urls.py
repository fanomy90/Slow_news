from django.contrib import admin
from django.urls import path, include
from news import views
# from news.views import page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),
    # path('settask/', views.TaskSetter.as_view()),
    # path('gettask/', views.TaskGetter.as_view()),
    # path('addtask/', views.AddTask, name="addTask"),
]
# handler404 = pageNotFound