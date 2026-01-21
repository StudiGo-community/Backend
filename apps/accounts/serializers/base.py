import re
from typing import Any

from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

"""
공통 필드 생성 및 검증 메서드
get_email_field: 아메일 필드
get_password_field: 비밀번호 필드
get_phone_field: 휴대폰 번호 필드
get_email_code_field: 이메일 인증 코드 필드 (base62 8자리)
get_phone_code_field: 휴대폰 인증 코드 필드 (숫자 6자리)
get_token_field: 검증 토큰 필드
get_nickname_field: 닉네임 필드
get_name_field: 이름 필드
validate_password_format: Django 비밀번호 검증 활용
validate_phone_format: 휴대폰 번호 형식 검증 (구상만)
validate_nickname_format: 닉네임 형식 검증 (구상만)
validate_phone_format: 휴대폰 번호 형식 검증 (숫자만, 하이픈 제거)
validate_nickname_format: 닉네임 형식 검증 (한글/영문/숫자만, 특수문자/공백 불가)
validate_email_code_format: 이메일 인증 코드 형식 검증 (영문+숫자, 8자리)
validate_phone_code_format: 휴대폰 인증 코드 형식 검증 (숫자만, 6자리)
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
            "min_length": 8,
            "max_length": 20,
            "style": {"input_type": "password"},
        }
        return serializers.CharField(**{**defaults, **kwargs})

    @staticmethod
    def get_phone_field(**kwargs: Any) -> serializers.CharField:
        defaults = {
            "required": True,
            "min_length": 10,
            "max_length": 15,
            "trim_whitespace": True,
        }
        return serializers.CharField(**{**defaults, **kwargs})

    @staticmethod
    def get_email_code_field(**kwargs: Any) -> serializers.CharField:
        defaults = {
            "required": True,
            "min_length": 8,
            "max_length": 8,
            "trim_whitespace": True,
        }
        return serializers.CharField(**{**defaults, **kwargs})

    @staticmethod
    def get_phone_code_field(**kwargs: Any) -> serializers.CharField:
        defaults = {
            "required": True,
            "min_length": 6,
            "max_length": 6,
            "trim_whitespace": True,
        }
        return serializers.CharField(**{**defaults, **kwargs})

    @staticmethod
    def get_token_field(**kwargs: Any) -> serializers.CharField:
        defaults = {"required": True}
        return serializers.CharField(**{**defaults, **kwargs})

    @staticmethod
    def get_nickname_field(**kwargs: Any) -> serializers.CharField:
        defaults = {
            "required": True,
            "min_length": 2,
            "max_length": 10,
            "trim_whitespace": True,
        }
        return serializers.CharField(**{**defaults, **kwargs})

    @staticmethod
    def get_name_field(**kwargs: Any) -> serializers.CharField:
        defaults = {
            "required": True,
            "max_length": 10,
            "trim_whitespace": True,
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
            raise serializers.ValidationError("휴대폰 번호는 숫자만 입력해주세요.")
        if not (10 <= len(cleaned) <= 15):
            raise serializers.ValidationError("휴대폰 번호 형식이 올바르지 않습니다.")
        return cleaned

    def validate_nickname_format(self, value: str) -> str:
        # 닉네임 형식 검증 (아직 협의필요)
        if not re.match(r"^[가-힣a-zA-Z0-9]+$", value):
            raise serializers.ValidationError(
                "닉네임은 한글, 영문, 숫자만 사용 가능합니다."
            )
        return value

    def validate_email_code_format(self, value: str) -> str:
        if not value.isalnum():
            raise serializers.ValidationError("인증 코드 형식이 올바르지 않습니다.")
        return value.upper()

    def validate_phone_code_format(self, value: str) -> str:
        if not value.isdigit():
            raise serializers.ValidationError("인증 번호는 숫자만 입력해주세요.")
        return value

    def validate_password_match(self, password: str, password_confirm: str) -> None:
        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )
