from __future__ import annotations

from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.accounts.utils.nickname_validator import validate_nickname
from apps.core.enumeration.account_user_enumeration import GenderChoices


class SignupRequestSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, max_length=20)
    password_confirm = serializers.CharField(
        write_only=True, min_length=8, max_length=20
    )

    nickname = serializers.CharField(min_length=2, max_length=12)
    name = serializers.CharField(max_length=10)
    gender = serializers.ChoiceField(choices=GenderChoices.choices)
    birthday = serializers.DateField(required=False, allow_null=True)

    agree_terms = serializers.BooleanField()
    agree_privacy = serializers.BooleanField()
    agree_marketing = serializers.BooleanField(required=False, default=False)

    # 닉네임 중복 확인/이메일 인증 토큰
    nickname_check_token = serializers.CharField(write_only=True)
    email_verify_token = serializers.CharField(write_only=True)

    def validate(self, attrs: Any) -> Any:
        # 비밀번호 확인
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"detail": "비밀번호가 일치하지 않습니다."}
            )

        # 비밀번호 유효성 검사
        try:
            validate_password(attrs["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"detail": e.messages[0]})

        # 닉네임 유효성 검사
        try:
            validate_nickname(attrs["nickname"])
        except Exception as e:
            msg = getattr(e, "message", None) or (
                e.messages[0] if hasattr(e, "messages") else str(e)
            )
            raise serializers.ValidationError({"detail": msg})

        # 필수 약관 동의
        if not attrs["agree_terms"] or not attrs["agree_privacy"]:
            raise serializers.ValidationError({"detail": "필수 약관에 동의해주세요."})

        return attrs


class SignupResponseSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nickname = serializers.CharField()
    name = serializers.CharField()
    gender = serializers.CharField()
    birthday = serializers.DateField(allow_null=True)
    created_at = serializers.DateTimeField()
