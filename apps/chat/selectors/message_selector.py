# 메시지 페이징 조회
from __future__ import annotations

from typing import Optional

from django.db.models import Prefetch, QuerySet

from apps.accounts.models import User
from apps.chat.models import Membership, Translation
from apps.chat.models.message import Message
from apps.chat.models.room import Room


def get_room_messages(
    *, room: Room, cursor: int | None, size: int
) -> QuerySet[Message]:
    qs = (
        Message.objects.filter(room=room)
        .select_related("sender__user")
        .prefetch_related(
            Prefetch(
                "translations",
                queryset=Translation.objects.only(
                    "message_id", "target_language", "translated_text"
                ),
            )
        )
        .order_by("-id")
    )

    if cursor is not None:
        qs = qs.filter(id__lt=cursor)

    return qs[: size + 1]


def get_active_membership(*, user: User, room: Room) -> Optional[Membership]:
    return (
        Membership.objects.select_related("room")
        .filter(user=user, room=room, left_at__isnull=True)
        .order_by("-joined_at")
        .first()
    )
