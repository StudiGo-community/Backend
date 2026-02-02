# 차단/해제/차단여부 판정
from __future__ import annotations

from typing import Optional

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from apps.chat.models.bans import Bans
from apps.chat.models.room import Room


@transaction.atomic
def create_ban(*, user_id: int, room_id: Optional[int], ends_at, reason: str | None = None) -> Bans:
    user = get_object_or_404(User, id=user_id)
    room = None
    if room_id is not None:
        room = get_object_or_404(Room, id=room_id)

    # 중복 방지(모델 constraint로도 막힘) + upsert 스타일로 처리
    obj, _created = Bans.objects.update_or_create(
        user=user,
        room=room,
        defaults={
            "ends_at": ends_at,
            "is_active": True,
        },
    )
    # reason 저장 안 하기로 했으니 패스(원하면 컬럼 추가 가능)
    return obj


@transaction.atomic
def update_ban(*, ban_id: int, is_active: bool | None, ends_at, reason: str | None = None) -> Bans:
    ban = get_object_or_404(Bans, id=ban_id)

    if is_active is not None:
        ban.is_active = is_active

    if ends_at is not None or ends_at is None:
        # ends_at 키가 들어오면(None 포함) 반영
        ban.ends_at = ends_at

    ban.save(update_fields=["is_active", "ends_at", "updated_at"])
    return ban
