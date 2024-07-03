import requests as r
import uuid #случайные имена файлов
import time
from celery import shared_task
from django.conf import settings #для генерации имен файлов
from random import randint
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import asyncio

# тестовые задачи для проверки работы вебсокетов
CAT_URL = "https://cataas.com/cat"
@shared_task
def download_a_cat():
    resp = r.get(CAT_URL)
    file_ext = resp.headers.get('Content-Type').split('/')[1]
    file_name = settings.BASE_DIR / 'SAVE' / (str(uuid.uuid4()) + "." + file_ext)
    with open(file_name, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=128):
            f.write(chunk)
    return True
@shared_task
def cpu_task1():
    time_to_sleep = randint(5, 10)
    time.sleep(time_to_sleep)
    return True
@shared_task(bind=True)
def cpu_task2(self):
    try:
        async def send_task_status():
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f"task_{self.request.id}",
                {"type": "task_status", "status": "PROGRESS", "message": f"I slept for {i + 1} seconds"},
            )
        time_to_sleep = randint(5, 10)
        for i in range(time_to_sleep):
            time.sleep(1)
            self.update_state(state="PROGRESS", meta={"current": i, "total": time_to_sleep})
            asyncio.get_event_loop().run_until_complete(send_task_status())
        return {"current": time_to_sleep, "total": time_to_sleep, "status": "SUCCESS"}
    except Exception as e:
        self.update_state(state="FAILURE", meta=str(e))
        return {"status": "FAILURE", "message": str(e)}