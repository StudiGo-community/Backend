from django.urls import path

from apps.chat.views.room_view import RoomListAPIView, RoomDetailAPIView

urlpatterns = [
    path("rooms", RoomListAPIView.as_view(), name="chat-room-list-create"),
    path("rooms/<int:room_id>", RoomDetailAPIView.as_view(), name="chat-room-detail"),
]
