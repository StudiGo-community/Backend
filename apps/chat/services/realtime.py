from __future__ import annotations

from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_room_event(*, room_id: int, event: dict[str, Any]) -> None:
    """
    REST/서비스에서 호출해도 500 안 나게 '안전하게' WS 브로드캐스트.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    group = f"room_{room_id}"
    try:
        async_to_sync(channel_layer.group_send)(group, event)
    except Exception:
        return
