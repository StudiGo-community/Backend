from typing import Any

from django.conf import settings
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.core.enumeration.account_verification_enumeration import (EmailVerificationPurpose, PhoneVerificationPurpose)

"""
공통 필드 생성 및 검증 메서드
get_email_field: 아메일 필드
get_password_field: 비밀번호 필드
get_phone_field: 휴대폰 번호 필드

get_verification_code_field: 인증 코드 빌드
get_token_field: 검증 토큰 필드
get_nickname_field: 닉네임 필드
get_name_field: 이름 필드
get_purpose_field: 인증 목적 필드



"""

class BaseMixin:

    @staticmethod
    def get_email_field(**kwargs: Any) -> serializers.EmailField:
        defaults = {"required": True, "max_length": 150}
        return serializers.EmailField(**{**defaults, **kwargs})

    @staticmethod
    def get_password_field(**kwargs: Any) -> serializers.CharField:
        defaults = {
            "required": True,
            "write_only": True,
            "max_length": 24,
            "style": {"input_type": "password"},
            }
        return serializers.CharField(**{**defaults, **kwargs})

    def validate_password_format(self, value: str) -> str:
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_phone_format(self, value: str) -> str:
        cleaned = value.replace("-", "").replace(" ", "")
        if not cleaned.isdigit():
            raise serializers.ValidationError("휴대폰 번호는 숫자만 입력해 주세요.")
        return cleaned