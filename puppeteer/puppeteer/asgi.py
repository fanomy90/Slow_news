import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import news.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puppeteer.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            news.routing.websocket_urlpatterns
        )
    ),
})
