# 방 목록/생성/상세 serializer
from rest_framework import serializers

from apps.chat.models.room import Room


class RoomSerializer(serializers.ModelSerializer[Room]):
    class Meta:
        model = Room
        fields = "__all__"


class RoomDetailSerializer(RoomSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class RoomCreateSerializer(RoomSerializer):
    name = serializers.CharField(max_length=20)
    description = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )
