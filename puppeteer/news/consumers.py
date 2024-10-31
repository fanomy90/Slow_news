import json
from channels.generic.websocket import AsyncWebsocketConsumer
from celery.result import AsyncResult
import uuid
import asyncio
from .tasks import cpu_task2, import_news_task
# from . import tasks
from news.task.parser_cisoclub import cisoclub_news
from news.task.parser_cisoclub_beat import cisoclub_news_beat
from news.task.parser_currency_beat import get_currency, currency_beat

# тестовая обработка работы с задачами
class SaveConsumer(AsyncWebsocketConsumer):
    task_status = {}
    # обработка подключения к вебсокетам
    async def connect(self):
        print("Client connected")
        await self.accept()
    # обработка сообщений полученных по вебсокетам
    async def receive(self, text_data):
        print(f"Received data: {text_data}")
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        task = text_data_json.get("task")
        
        if message_type == "start_task" and task:
            task_id = str(uuid.uuid4())
            # запуск основного скрипта парсера данных
            if task == "task1":
                cisoclub_news.apply_async(kwargs={'mode': 'security'}, task_id=task_id)
            # запуск импорта новостей
            elif task == "task2":
                import_news_task.apply_async(args=[], task_id=task_id)
            # запуск основного тестовой задачи для проверки вывода сообщений
            elif task == "task3":
                cpu_task2.apply_async(args=[], task_id=task_id)
            elif task == "task4":
                cisoclub_news.apply_async(kwargs={'mode': 'public'}, task_id=task_id)
            elif task == "task5":
                cisoclub_news.apply_async(kwargs={'mode': 'review'}, task_id=task_id)
            elif task == "task6":
                cisoclub_news.apply_async(kwargs={'mode': 'interviews'}, task_id=task_id)
            elif task == "task7":
                cisoclub_news_beat.apply_async(kwargs={'mode': 'security'}, task_id=task_id)
            elif task == "task8":
                # get_currency.apply_async(kwargs={'mode': 'rub'}, task_id=task_id)
                currency_beat.apply_async(kwargs={'mode': 'rub'}, task_id=task_id)
            self.task_status[task_id] = "PENDING"
            while True:
                status = AsyncResult(task_id).state
                if self.task_status[task_id] != status:
                    self.task_status[task_id] = status
                    await self.send(text_data=json.dumps({"task_id": task_id, "status": status}))
                if status in ("SUCCESS", "FAILURE"):
                    break
                await asyncio.sleep(3)
    # обработка выполнения задачи и передача сообщения по вебсокетам на фронт
    async def task_is_complete(self, task_id):
        status = AsyncResult(task_id).state
        return status in ("SUCCESS", "FAILURE")
    # обработка отключения от вебсокета
    async def disconnect(self, close_code):
        pass

class ComTaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем ID задачи из URL пути
        task_id = self.scope['url_route']['kwargs']['task_id']
        self.task_group_name = f"task_{task_id}"
        # Присоединяемся к группе WebSocket
        await self.channel_layer.group_add(
            self.task_group_name,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self, close_code):
        # Отсоединяемся от группы WebSocket
        await self.channel_layer.group_discard(
            self.task_group_name,
            self.channel_name
        )
    # Обработка сообщений от WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        task = text_data_json.get("task")
        if message_type == "start_task" and task:
            # Здесь вы можете добавить логику для запуска задачи в зависимости от типа задачи
            pass
    # Обработка сообщений группы WebSocket
    async def task_status(self, event):
        status = event['status']
        message = event['message']
        #task_id = event['task_id']
        task_id = self.scope['url_route']['kwargs']['task_id']
        # Отправляем обновление состояния задачи клиенту
        #await self.send(text_data=json.dumps({"status": status, "message": message}))
        await self.send(text_data=json.dumps({"task_id": task_id, "status": status, "message": message}))