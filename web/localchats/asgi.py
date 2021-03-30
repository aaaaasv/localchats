import os

from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import geochats.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "localchats.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            geochats.routing.websocket_urlpatterns
        )
    ),
})