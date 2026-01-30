from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.accounts.models import User
from apps.chat.models.message import Message


@transaction.atomic
def admin_delete_message(*, admin: User, message_id: int) -> Message:
    msg = get_object_or_404(Message, pk=message_id)

    # 이미 삭제된 메시지는  200 OK
    if msg.status != Message.Status.DELETED_BY_ADMIN:
        msg.status = Message.Status.DELETED_BY_ADMIN
        # updated_at 자동 갱신
        msg.save(update_fields=["status", "updated_at"])

        # 실시간 제거
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_room_{msg.room_id}",
            {
                "type": "message.deleted",
                "room_id": msg.room_id,
                "message_id": msg.id,
            },
        )

    return msg
