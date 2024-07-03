from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/start_task/$", consumers.SaveConsumer.as_asgi()),
    re_path(r"ws/start_task/(?P<task_id>[\w-]+)/$", consumers.SaveConsumer.as_asgi()),
]