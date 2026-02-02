from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.accounts.utils.normalize_phone import normalize_phone


class FindEmailRequestSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(max_length=10)
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value: str) -> str:
        normalized = normalize_phone(value)
        if len(normalized) < 9:
            raise serializers.ValidationError("휴대폰번호 형식이 올바르지 않습니다.")
        return normalized


class FindEmailResponseSerializer(serializers.Serializer[Any]):
    email = serializers.CharField()
