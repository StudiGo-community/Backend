# apps/chat/serializers/message_serializer.py
from __future__ import annotations

from typing import Any, Iterable

from rest_framework import serializers

from apps.chat.models.message import Message
from apps.chat.models.translation import Translation


class SenderUserSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    profile_image_url = serializers.CharField(allow_null=True)


class MessageListSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    sender_user_id = serializers.IntegerField(source="sender.user.id")
    sender = SenderUserSerializer(source="sender.user", read_only=True)

    ko_content = serializers.SerializerMethodField()
    es_content = serializers.SerializerMethodField()

    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    def _get_sender(self, obj: Message) -> dict[str, Any]:
        u = obj.sender.user
        return {
            "id": getattr(u, "id", None),
            "nickname": getattr(u, "nickname", None),
            "profile_image_url": getattr(u, "profile_image_url", None),
        }

    def _get_translations(self, obj: Message) -> Iterable[Translation]:

        # 1) related_name="translations" 케이스
        rel = getattr(obj, "translations", None)
        if rel is not None and hasattr(rel, "all"):
            return rel.all()

        # 2) related_name 지정 안 한 기본 케이스
        rel2 = getattr(obj, "translation_set", None)
        if rel2 is not None and hasattr(rel2, "all"):
            return rel2.all()

        return []

    def _translation_map(self, obj: Message) -> dict[str, str]:
        m: dict[str, str] = {}
        for t in self._get_translations(obj):
            m[t.target_language] = t.translated_text
        return m

    def get_ko_content(self, obj: Message) -> str:
        m = self._translation_map(obj)
        return m.get("ko") or obj.content

    def get_es_content(self, obj: Message) -> str | None:
        m = self._translation_map(obj)
        return m.get("es")


class MessageCreateSerializer(serializers.Serializer[Any]):
    content = serializers.CharField()


class MessageDetailSerializer(serializers.Serializer[Any]):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    results = MessageListSerializer(many=True)
