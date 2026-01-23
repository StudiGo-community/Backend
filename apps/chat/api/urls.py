from django.urls import path

from apps.chat.views.room_view import RoomDetailAPIView, RoomListAPIView

urlpatterns = [
    path("chat/rooms", RoomListAPIView.as_view(), name="chat-room-list-create"),
    path("chat/rooms/<int:room_id>", RoomDetailAPIView.as_view(), name="chat-room-detail"),
]
