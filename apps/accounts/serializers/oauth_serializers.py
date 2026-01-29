from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.services.check_nickname_services import (
    normalize_nickname,
    verify_nickname_check_token,
)
from apps.accounts.utils.nickname_validator import validate_nickname


class SocialSignupCompleteRequestSerializer(serializers.Serializer[Any]):
    session_id = serializers.CharField()

    nickname = serializers.CharField()
    nickname_check_token = serializers.CharField()

    gender = serializers.ChoiceField(choices=("M", "F"))
    phone = serializers.CharField()

    agree_terms = serializers.BooleanField()
    agree_privacy = serializers.BooleanField()
    agree_marketing = serializers.BooleanField(required=False, default=False)

    def validate_nickname(self, value: str) -> str:
        value = normalize_nickname(value)
        validate_nickname(value)
        return value

    def validate_phone(self, value: str) -> str:
        digits = "".join(num for num in value if num.isdigit())
        if not digits:
            raise serializers.ValidationError({"detail": "요청값이 올바르지 않습니다."})
        return digits

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs["agree_terms"] or not attrs["agree_privacy"]:
            raise serializers.ValidationError(
                {"detail": "필수 약관에 동의해야 회원가입이 가능합니다."}
            )

        ok = verify_nickname_check_token(
            nickname=attrs["nickname"],
            check_token=attrs["nickname_check_token"],
            consume=True,
        )
        if not ok:
            raise serializers.ValidationError(
                {"detail": "닉네임 중복 확인을 다시 진행해주세요."}
            )

        User = get_user_model()
        if User.objects.filter(phone=attrs["phone"]).exists():
            raise serializers.ValidationError(
                {"detail": "이미 등록된 휴대폰 번호입니다."}
            )

        return attrs


class SocialLinkConfirmRequestSerializer(serializers.Serializer[Any]):
    session_id = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


class TokenPayloadSerializer(serializers.Serializer[Any]):
    access_token = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")
    expires_in = serializers.IntegerField()


class SocialAuthUserSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nickname = serializers.CharField()


class SocialAuthSResponseSerializer(serializers.Serializer[Any]):
    token = TokenPayloadSerializer()
    user = SocialAuthUserSerializer()
