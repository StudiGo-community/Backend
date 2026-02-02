# 차단/해제/차단여부 판정
from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.accounts.models import User
from apps.chat.models.bans import Bans
from apps.chat.models.room import Room


def is_banned(*, user_id: int, room_id: int | None = None) -> bool:
    """
    활성 차단 여부
    - 글로벌 차단(room IS NULL) 또는
    - 특정 방 차단(room_id 일치) 중 하나라도 걸리면 True
    """
    now = timezone.now()

    qs = Bans.objects.filter(
        user_id=user_id,
        is_active=True,
    ).filter(models.Q(ends_at__isnull=True) | models.Q(ends_at__gt=now))

    if room_id is None:
        return qs.filter(room__isnull=True).exists()
    return qs.filter(models.Q(room__isnull=True) | models.Q(room_id=room_id)).exists()


@transaction.atomic
def create_ban(
    *,
    admin: User,
    user_id: int,
    room_id: int | None,
    ends_at: datetime | None,
    reason: str | None = None,
) -> Bans:
    user = get_object_or_404(User, id=user_id)
    room = None
    if room_id is not None:
        room = get_object_or_404(Room, id=room_id)

    # 중복 방지
    obj, _created = Bans.objects.update_or_create(
        admin=admin,
        user=user,
        room=room,
        defaults={
            "ends_at": ends_at,
            "is_active": True,
        },
    )
    return obj


@transaction.atomic
def update_ban(
    *,
    ban_id: int,
    is_active: bool | None = None,
    ends_at: datetime | None = None,
    reason: str | None = None,
) -> Bans:
    ban = get_object_or_404(Bans, id=ban_id)

    if is_active is not None:
        ban.is_active = is_active

    ban.ends_at = ends_at

    ban.save(update_fields=["is_active", "ends_at", "updated_at"])
    return ban
