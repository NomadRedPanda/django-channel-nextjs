# chat/routing.py
from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    # path('ws/chat/enola', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]