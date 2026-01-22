from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.accounts.models.users import User


class LoginRequestSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)
    remember_me = serializers.BooleanField(required=False, default=False)


class LoginResponseSerializer(serializers.Serializer[Any]):
    # token
    access_token = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")
    expires_in = serializers.IntegerField()

    # user
    user = serializers.SerializerMethodField()

    def get_user(self, obj: dict[str, Any]) -> dict[str, Any]:
        user: User = obj["user"]
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "name": user.name,
            "profile_image_url": user.profile_image_url,
            "role": user.role,
            "status": user.status,
        }
