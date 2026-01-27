from __future__ import annotations

from typing import Any

from rest_framework import serializers


class CheckEmailRequestSerializer(serializers.Serializer[Any]):
    email = serializers.CharField()


class CheckNicknameRequestSerializer(serializers.Serializer[Any]):
    nickname = serializers.CharField()


class CheckResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField()
    check_token = serializers.CharField(required=False)
    expires_in = serializers.IntegerField(required=False)
