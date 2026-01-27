# 메세지 조회 / 삭제
from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.chat.models.message import Message


class MessageListSerializer(serializers.ModelSerializer[Message]):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    room_id = serializers.IntegerField(source="room.id", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "room_id",
            "sender_id",
            "content",
            "status",
            "created_at",
        ]

class MessageCreateSerializer(serializers.Serializer[Any]):
    content = serializers.CharField()

class MessageDetailSerializer(MessageListSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = fields