# 입장/퇴장 serializer(요청/응답)
from __future__ import annotations

from rest_framework import serializers

from apps.chat.models.room import Room


class RoomJoinResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    room = serializers.SerializerMethodField()

    def get_room(self, obj: Room) -> dict:
        return {
            "id": obj.id,
            "name": obj.name,
        }
