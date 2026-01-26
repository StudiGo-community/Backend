from __future__ import annotations

from typing import Any, Dict

from rest_framework import serializers

BASE62_8_REGEX = r"^[0-9A-Za-z]{8}$"


class ResetPasswordEmailSendCodeRequestSerializer(
    serializers.Serializer[Dict[str, Any]]
):
    email = serializers.EmailField(required=True, write_only=True)


class SignupEmailSendCodeRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    """
    - check_email API에서 받은 check_token 필수
    """

    email = serializers.EmailField(required=True, write_only=True)
    check_token = serializers.CharField(required=True, write_only=True)


class EmailSendCodeResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    request_id = serializers.CharField(help_text="인증 요청 식별자")
    expires_in = serializers.IntegerField(help_text="인증코드 만료까지 남은 시간(초)")
    cooldown = serializers.IntegerField(help_text="재전송 가능까지 남은 시간(초)")


class EmailConfirmCodeRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    email = serializers.EmailField(required=True, write_only=True)
    request_id = serializers.CharField(required=True, write_only=True)
    verification_code = serializers.RegexField(
        BASE62_8_REGEX,
        required=True,
        write_only=True,
        help_text="base62 8자리 인증코드",
    )


class EmailConfirmCodeResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    email_verify_token = serializers.CharField(
        help_text="다음 단계에서 1회용으로 소비할 검증 토큰"
    )
    expires_in = serializers.IntegerField(help_text="토큰 만료까지 남은 시간(초)")
