import os
from celery import Celery
from celery.signals import worker_ready  # Импортируем worker_ready
#from news.tasks import run_bot  # Импортируйте вашу задачу

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puppeteer.settings')
app = Celery('puppeteer')
# Настройки Celery будут автоматически браться из настроек Django, если указать ниже.
app.config_from_object('django.conf:settings', namespace='CELERY')
# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()
# app.autodiscover_tasks(['news.task'])

app.conf.broker_connection_retry_on_startup = True

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print('Request: {}'.format(self.request))

# убрал чтобы запуск шел через Supervisor.
# @worker_ready.connect
# def start_bot(sender, **kwargs):
#     from news.tasks import run_bot  # Отложенный импорт здесь
#     run_bot.delay()  # Запускаем бота как задачу