# 채팅 consumer (send/receive)
from __future__ import annotations

import json
from typing import Any

import logging
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from apps.chat.models import Membership

logger = logging.getLogger(__name__)


@sync_to_async
def _has_active_membership(user_id: int, room_id: int) -> bool:
    return Membership.objects.filter(
        user_id=user_id,
        room_id=room_id,
        left_at__isnull=True,
    ).exists()


class ChatConsumer(AsyncWebsocketConsumer):  # type: ignore[misc]
    async def connect(self) -> None:
        user = self.scope.get("user")

        # 1) 인증 체크
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            logger.warning("WS connect rejected: unauthenticated")
            await self.close(code=4001)  # unauthorized
            return

        # 2) room_id 파싱
        room_id_raw = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_id = int(room_id_raw)
        self.group_name = f"room_{self.room_id}"

        # 3) 입장 상태 체크(REST에서 join 성공한 사람만 WS 붙게)
        ok = await _has_active_membership(user.id, self.room_id)
        if not ok:
            logger.warning(
                "WS connect rejected: not joined user_id=%s room_id=%s",
                user.id,
                self.room_id,
            )
            await self.close(code=4003)  # forbidden (not joined)
            return

        # 4) 그룹 join + accept
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # 연결 확인 메시지
        await self.send_json(
            {
                "type": "system",
                "message": "connected",
                "room_id": self.room_id,
            }
        )

    async def disconnect(self, close_code: int) -> None:
        logger.info("WS disconnected: room_id=%s code=%s", getattr(self, "room_id", None), close_code)
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(
        self, text_data: str | None = None, bytes_data: bytes | None = None
    ) -> None:
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        if not text_data:
            return

        payload = json.loads(text_data)
        content = (payload.get("content") or "").strip()
        if not content:
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "room_id": self.room_id,
                "sender_id": user.id,
                "content": content,
                "sent_at": timezone.now().isoformat(),
            },
        )

    async def chat_message(self, event: dict[str, Any]) -> None:
        await self.send_json(
            {
                "type": "message",
                "room_id": event["room_id"],
                "sender_id": event["sender_id"],
                "content": event["content"],
                "sent_at": event["sent_at"],
            }
        )

    async def message_deleted(self, event: dict[str, Any]) -> None:
        await self.send_json(
            {
                "type": "MESSAGE_DELETED",
                "room_id": event["room_id"],
                "message_id": event["message_id"],
            }
        )

    async def send_json(self, data: dict[str, Any]) -> None:
        await self.send(text_data=json.dumps(data, ensure_ascii=False))
