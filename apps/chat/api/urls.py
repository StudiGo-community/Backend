from django.urls import path

from apps.chat.models import MessageReport
from apps.chat.views.membership_view import ChatRoomExitAPIView, ChatRoomJoinAPIView
from apps.chat.views.message_report_view import MessageReportCreateAPIView
from apps.chat.views.message_view import MessageListAPIView
from apps.chat.views.room_view import RoomDetailAPIView, RoomListAPIView

urlpatterns = [
    path("chat", RoomListAPIView.as_view(), name="chat-room-list"),
    path(
        "chat/rooms/<int:room_id>",
        RoomDetailAPIView.as_view(),
        name="chat-room-detail",
    ),
    path("chat/<int:room_id>", ChatRoomJoinAPIView.as_view(), name="chat-room-join"),
    path(
        "chat/<int:room_id>/exit", ChatRoomExitAPIView.as_view(), name="chat-room-exit"
    ),
    path(
        "chat/<int:room_id>/messages",
        MessageListAPIView.as_view(),
        name="chat-message-list",
    ),
    path(
        "chat/messages/<int:message_id>/report",
        MessageReportCreateAPIView.as_view(),
        name="chat-message-report",
    ),
]
