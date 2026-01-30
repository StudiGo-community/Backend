# 방 목록/상세 serializer
from rest_framework import serializers

from apps.chat.models.room import Room


class RoomSerializer(serializers.ModelSerializer[Room]):
    class Meta:
        model = Room
        fields = "__all__"


class RoomDetailSerializer(RoomSerializer):
    pass
