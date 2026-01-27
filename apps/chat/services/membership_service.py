# 입장/퇴장 + “다른 방 접속 중이면 거부”
from __future__ import annotations

from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.accounts.models import User
from apps.chat.models.bans import Bans
from apps.chat.models.membership import Membership
from apps.chat.models.room import Room

def _is_banned(*, user: User, room: Room) -> bool:
    now = timezone.now()
    return Bans.objects.filter(
        user=user,
        is_active=True,
    ).filter(
        Q(room__isnull=True) | Q(room=room)
    ).filter(
        Q(ends_at__isnull=True) | Q(ends_at__gt=now)
    ).exists()

def join_room(*, user, room_id: int) -> Room:
    """
    명세:
    - 이미 다른 채팅방에 접속 중(left_at is null) 이면 403
    - 차단된 사용자면 403
    - 성공 시 membership 생성 + participant_count +1
    """
    now = timezone.now()

    # 방 존재 체크 (404)
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        raise NotFound("채팅방을 찾을 수 없습니다.")

    # 차단 체크 (403)
    is_banned = Bans.objects.filter(
        user=user,
        is_active=True,
    ).filter(
        Q(ends_at__isnull=True) | Q(ends_at__gt=now)
    ).filter(
        Q(room__isnull=True) | Q(room=room)
    ).exists()

    if is_banned:
        raise PermissionDenied("채팅 이용이 제한된 사용자입니다.")

    # 동시 접속 체크 (403)
    already_in_room = Membership.objects.filter(user=user, left_at__isnull=True).exists()
    if already_in_room:
        raise PermissionDenied("이미 다른 채팅방에 접속 중입니다.")

    # 입장 처리(트랜잭션)
    with transaction.atomic():
        # membership 생성
        Membership.objects.create(user=user, room=room)

        # participant_count +1 (원자적 업데이트)
        Room.objects.filter(pk=room.pk).update(participant_count=F("participant_count") + 1)

        # 최신 값 다시 로드해서 반환
        room.refresh_from_db(fields=["participant_count"])

    return room


@transaction.atomic
def exit_room(*, user: User, room: Room) -> Membership:
    # room row도 잠가서 count 경쟁 줄이기
    room = Room.objects.select_for_update().get(pk=room.pk)

    membership = (
        Membership.objects.select_for_update()
        .filter(user=user, room=room, left_at__isnull=True)
        .first()
    )
    if membership is None:
        raise ValueError("이미 퇴장했거나 현재 입장 중이 아닙니다.")

    membership.left_at = timezone.now()
    membership.save(update_fields=["left_at"])

    # 음수 방지
    Room.objects.filter(pk=room.pk, participant_count__gt=0).update(
        participant_count=F("participant_count") - 1
    )

    return membership