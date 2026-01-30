from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from apps.chat.models.message import Message


@transaction.atomic
def admin_delete_message(*, admin: User, room_id: int, message_id: int) -> Message:
    msg = get_object_or_404(Message, id=message_id, room_id=room_id)

    # 이미 삭제된 메시지는  200 OK
    if msg.status != Message.Status.DELETED_BY_ADMIN:
        msg.status = Message.Status.DELETED_BY_ADMIN
        msg.save(update_fields=["status", "updated_at"])
    return msg
