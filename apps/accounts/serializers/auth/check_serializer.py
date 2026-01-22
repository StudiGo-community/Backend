from typing import Any

from rest_framework import serializers

from apps.accounts.serializers.base import BaseMixin

"""
[중복확인]
EmailCheckSerializer
이메일 중복 확인
    POST /api/v1/auth/check-email

EmailCheckResponseSerializer
이메일 중복 확인 응답

NicknameCheckSerializer
닉네임 중복 확인
    POST /api/v1/auth/check-nickname

NicknameCheckResponseSerializer
닉네임 중복 확인 응답
"""

class EmailCheckSerializer(serializers.Serializer[Any], BaseMixin):
    email = BaseMixin.get_email_field()

class EmailCheckResponseSerializer(serializers.Serializer[Any]):
    available = serializers.BooleanField()
    message = serializers.CharField()

class NicknameCheckSerializer(serializers.Serializer[Any], BaseMixin):
    nickname = BaseMixin.get_nickname_field()

    def validate_nickname(self, value: str) -> str:
        return self.validate_nickname_format(value)

class NicknameCheckResponseSerializer(serializers.Serializer[Any]):
    available = serializers.BooleanField()
    message = serializers.CharField()
