# 메시지 페이징 조회
from __future__ import annotations

from typing import Optional

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.chat.models import Membership
from apps.chat.models.message import Message
from apps.chat.models.room import Room


def get_room_messages(*, room: Room) -> QuerySet[Message]:
    return (
        Message.objects.filter(room=room)
        .select_related("sender", "room")
        .order_by("-created_at")
    )

def get_active_membership(*, user: User, room: Room) -> Optional[Membership]:
    return (
        Membership.objects.select_related("room")
        .filter(user=user, room=room, left_at__isnull=True)
        .order_by("-joined_at")
        .first()
    )