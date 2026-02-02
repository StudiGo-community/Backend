from __future__ import annotations

from django.db import IntegrityError, transaction

from apps.accounts.models import User
from apps.chat.models.message import Message
from apps.chat.models.message_report import MessageReport
from apps.chat.services.message_service import assert_can_read_room_messages


@transaction.atomic
def report_message(*, user: User, message: Message, reason: str) -> None:
    # 멤버십이 있어야 신고 가능
    assert_can_read_room_messages(user=user, room=message.room)

    try:
        MessageReport.objects.create(
            message=message,
            reporter=user,
            reason=reason,
        )
    except IntegrityError:
        # 같은 메시지 중복 신고 무시
        pass
