# 입장/퇴장 serializer(요청/응답)
from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.chat.models.room import Room


class RoomSummarySerializer(serializers.ModelSerializer[Room]):
    class Meta:
        model = Room
        fields = ["id", "name"]


class RoomJoinResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField()
    room = serializers.SerializerMethodField()


class RoomExitResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField()
