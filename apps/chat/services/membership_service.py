from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.utils import timezone

from apps.accounts.models import User
from apps.chat.models.bans import Bans
from apps.chat.models.membership import Membership
from apps.chat.models.room import Room


def _now() -> datetime:
    return timezone.now()


def _is_user_banned(*, user: User, room: Room) -> bool:
    now = _now()
    return (
        Bans.objects.filter(
            user=user,
            is_active=True,
        )
        .filter(
            Q(room__isnull=True) | Q(room=room),
            Q(ends_at__isnull=True) | Q(ends_at__gt=now),
        )
        .exists()
    )


def _get_active_membership(*, user: User) -> Optional[Membership]:
    # left_at이 null이면 현재 “입장 중”
    return (
        Membership.objects.select_related("room")
        .filter(user=user, left_at__isnull=True)
        .order_by("-joined_at")
        .first()
    )


@transaction.atomic  ## <- 이거 왜??
def join_room(*, user: User, room: Room) -> Membership:
    """
    - 차단 사용자 입장 불가
    - 이미 다른 방에 입장 중이면 입장 불가
    - 성공 시 membership 생성 + room.participant_count +1
    """
    if _is_user_banned(user=user, room=room):
        raise PermissionError("채팅 이용이 제한된 사용자입니다.")

    active = _get_active_membership(user=user)
    if active is not None:
        # 같은 방 재입장은 정책상 “이미 입장 중”으로 보든, idempotent로 보든 선택인데
        # 명세가 '다른 방이면 거부'라서, 같은 방이면 그대로 통과(기존 membership 반환)로 처리 가능
        if active.room_id != room.id:
            raise PermissionError("이미 다른 채팅방에 접속 중입니다.")
        return active

    try:
        membership = Membership.objects.create(
            user=user,
            room=room,
            joined_at=_now(),
            left_at=None,
        )
    except IntegrityError:
        # 동시 요청 등으로 인한 중복 멤버십 생성 시도 시, 기존 활성 멤버십 반환
        existing = Membership.objects.filter(
            user=user, room=room, left_at__isnull=True
        ).first()
        if existing:
            return existing
        raise

    # 동시성 고려해서 F() 업데이트
    Room.objects.filter(id=room.id).update(participant_count=F("participant_count") + 1)
    return membership


@transaction.atomic
def exit_room(*, user: User, room: Room) -> None:
    """
    - 해당 방에 '입장 중인 membership(left_at is null)'이 있어야 퇴장 가능
    - 성공 시 membership.left_at 업데이트 + room.participant_count -1
    """
    membership = (
        Membership.objects.select_for_update()
        .filter(user=user, room=room, left_at__isnull=True)
        .order_by("-joined_at")
        .first()
    )

    if membership is None:
        raise ValueError("이미 퇴장한 상태입니다.")

    membership.left_at = _now()
    membership.save(update_fields=["left_at"])

    Room.objects.filter(id=room.id).update(participant_count=F("participant_count") - 1)
