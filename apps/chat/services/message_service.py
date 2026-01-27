# 메시지 저장/삭제(관리자), last_message_at 갱신
from __future__ import annotations

from django.utils import timezone
from django.db.models import Q

from apps.accounts.models.users import User
from apps.chat.models.bans import Bans
from apps.chat.models.membership import Membership
from apps.chat.models.room import Room


def _is_banned(*, user: User, room: Room) -> bool:
    now = timezone.now()
    return Bans.objects.filter(user=user, is_active=True).filter(
        Q(room__isnull=True) | Q(room=room)
    ).filter(
        Q(ends_at__isnull=True) | Q(ends_at__gt=now)
    ).exists()


def assert_can_read_room_messages(*, user: User, room: Room) -> None:
    # 1) 차단이면 조회도 막기(명세에 따라)
    if _is_banned(user=user, room=room):
        raise PermissionError("채팅 이용이 제한된 사용자입니다.")

    # 2) “퇴장 후 기록 조회 불가” => 현재 active membership이 있어야만 조회 허용
    is_active_member = Membership.objects.filter(
        user=user, room=room, left_at__isnull=True
    ).exists()
    if not is_active_member:
        raise PermissionError("채팅방에 입장한 상태에서만 메시지를 조회할 수 있습니다.")
