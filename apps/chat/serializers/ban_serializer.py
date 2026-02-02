# 차단/해제
from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User
from apps.chat.models.bans import Bans
from apps.chat.models.room import Room


class BanSerializer(serializers.ModelSerializer[Bans]):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    room_id = serializers.IntegerField(source="room.id", allow_null=True, read_only=True)

    # 응답 is_active는 "활성판정"으로 내려주고 싶으면 SerializerMethodField로 바꿔도 됨
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Bans
        fields = ["id", "user_id", "room_id", "ends_at", "is_active", "created_at", "updated_at"]

    def get_is_active(self, obj: Bans) -> bool:
        if not obj.is_active:
            return False
        if obj.ends_at is None:
            return True
        return obj.ends_at > timezone.now()


class BanCreateSerializer(serializers.Serializer[Any]):
    user_id = serializers.IntegerField()
    room_id = serializers.IntegerField(required=False, allow_null=True)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True)  # 지금은 저장 안 해도 받기만

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # user 존재 확인
        user_id = attrs["user_id"]
        if not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError({"detail": "사용자를 찾을 수 없습니다."})

        # room 존재 확인(있을 때만)
        room_id = attrs.get("room_id", None)
        if room_id is not None and not Room.objects.filter(id=room_id).exists():
            raise serializers.ValidationError({"detail": "채팅방을 찾을 수 없습니다."})

        return attrs


class BanUpdateSerializer(serializers.Serializer[Any]):
    is_active = serializers.BooleanField(required=False)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if "is_active" not in attrs and "ends_at" not in attrs:
            raise serializers.ValidationError({"detail": "수정할 값이 없습니다."})
        return attrs


class BanListResponseSerializer(serializers.Serializer[Any]):
    items = BanSerializer(many=True)
    page = serializers.IntegerField()
    total = serializers.IntegerField()
