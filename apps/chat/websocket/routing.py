# ws URL 패턴
from django.urls import re_path

from apps.chat.websocket.consumers.chat import ChatConsumer

websocket_urlpatterns = [
    re_path(r"^ws/chat/rooms/(?P<room_id>\d+)/$", ChatConsumer.as_asgi()),
]
