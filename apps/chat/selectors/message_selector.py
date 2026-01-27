# 메시지 페이징 조회
from __future__ import annotations

from django.db.models import QuerySet

from apps.chat.models.message import Message
from apps.chat.models.room import Room


def get_room_messages(*, room: Room) -> QuerySet[Message]:
    return (
        Message.objects.filter(room=room)
        .select_related("sender", "room")
        .order_by("-created_at")
    )
