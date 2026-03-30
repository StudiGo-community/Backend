# 차단 목록/현재 차단 여부 조회
from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import User
from apps.chat.models.bans import Bans
from apps.chat.models.room import Room


def active_ban_q() -> Q:
    now = timezone.now()
    return Q(is_active=True) & (Q(ends_at__isnull=True) | Q(ends_at__gt=now))


def is_user_banned(*, user: User, room: Room) -> bool:
    # 1) 전체 차단
    if (
        Bans.objects.filter(user=user, room__isnull=True)
        .filter(active_ban_q())
        .exists()
    ):
        return True

    # 2) 특정 방 차단
    return Bans.objects.filter(user=user, room=room).filter(active_ban_q()).exists()
