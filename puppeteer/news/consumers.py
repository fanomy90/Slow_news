import json
from channels.generic.websocket import AsyncWebsocketConsumer
from celery.result import AsyncResult
import uuid
import asyncio
from .tasks import download_a_cat, cpu_task1, download_a_news
# from . import tasks

# тестовая обработка работы с задачами
class SaveConsumer(AsyncWebsocketConsumer):
    task_status = {}

    # обработка подключения к вебсокетам
    async def connect(self):
        await self.accept()

    # обработка сообщений полученных по вебсокетам
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        task = text_data_json.get("task")
        
        if message_type == "start_task" and task:
            task_id = str(uuid.uuid4())
            
            if task == "task1":
                download_a_news.apply_async(args=[], task_id=task_id)
            elif task == "task2":
                # нерабочий пример задачи с передачей сообщений статуса
                # cpu_task2.apply_async(args=[], task_id=task_id)
                cpu_task1.apply_async(args=[], task_id=task_id)

            elif task == "task3":
                download_a_cat.apply_async(args=[], task_id=task_id)
            self.task_status[task_id] = "PENDING"
            while True:
                status = AsyncResult(task_id).state
                if self.task_status[task_id] != status:
                    self.task_status[task_id] = status
                    await self.send(text_data=json.dumps({"task_id": task_id, "status": status}))
                
                if status in ("SUCCESS", "FAILURE"):
                    break
                
                await asyncio.sleep(1)

    # обработка выполнения задачи и передача сообщения по вебсокетам на фронт
    async def task_is_complete(self, task_id):
        status = AsyncResult(task_id).state
        return status in ("SUCCESS", "FAILURE")

    # обработка отключения от вебсокета
    async def disconnect(self, close_code):
        pass
