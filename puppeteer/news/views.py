from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from . import tasks
from celery.result import AsyncResult
from rest_framework.views import APIView
from news.tasks import cpu_task1, cpu_task2
from django.shortcuts import render

# домашняя страница
def home(request):
    tasks.download_a_cat.delay()
    return HttpResponse('<g1>Гружу кота</h1>')
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