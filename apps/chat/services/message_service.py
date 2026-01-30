# 메시지 저장/삭제(관리자), last_message_at 갱신
from __future__ import annotations

from datetime import datetime

from django.db import transaction as db_transaction
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models.users import User
from apps.chat.models import Message, Translation
from apps.chat.models.bans import Bans
from apps.chat.models.membership import Membership
from apps.chat.models.room import Room
from apps.chat.selectors.message_selector import get_active_membership
from apps.core.translation import translate_es_to_ko, translate_ko_to_es


def _is_banned(*, user: User, room: Room) -> bool:
    now = timezone.now()
    return (
        Bans.objects.filter(user=user, is_active=True)
        .filter(Q(room__isnull=True) | Q(room=room))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gt=now))
        .exists()
    )


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


def _now() -> datetime:
    return timezone.now()


def _assert_can_send_message(*, user: User, room: Room) -> None:
    now = _now()

    # ban 체크
    banned = (
        Bans.objects.filter(user=user, is_active=True)
        .filter(Q(room__isnull=True) | Q(room=room))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gt=now))
        .exists()
    )
    if banned:
        raise PermissionError("채팅 이용이 제한된 사용자 입니다")

    membership = Membership.objects.filter(user=user, room=room)
    if membership is None:
        raise PermissionError("채팅방에 입장한 사용자만 메세지를 보낼 수 있습니다")


@db_transaction.atomic
def send_message(*, user: User, room: Room, content: str) -> Message:
    membership = get_active_membership(user=user, room=room)
    if membership is None:
        raise PermissionError("채팅방에 입장한 사용자만 메세지를 보낼 수 있습니다")

    # 메세지 보내기
    msg = Message.objects.create(
        sender=membership, room=room, content=content, status=Message.Status.SENT
    )

    # 언어 판별
    is_korean = any("가" <= ch <= "힣" for ch in content)

    translations: list[Translation] = []

    if is_korean:
        ko_text = content
        es_text = translate_ko_to_es(content)
    else:
        es_text = content
        ko_text = translate_es_to_ko(content)

    # 번역 저장
    Translation.objects.update_or_create(
        message=msg,
        target_language="ko",
        defaults={"translated_text": ko_text},
    )
    Translation.objects.update_or_create(
        message=msg,
        target_language="es",
        defaults={"translated_text": es_text},
    )

    # 채팅방 갱신
    Room.objects.filter(id=room.id).update(last_message_at=_now())

    return msg
