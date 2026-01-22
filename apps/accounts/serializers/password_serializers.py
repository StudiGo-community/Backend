from typing import Any

from rest_framework import serializers

from apps.accounts.models.users import User
from apps.accounts.serializers.base import BaseMixin

"""
비밀번호 찾기

PasswordResetSendCodeSerializer
이메일 인증 발송
    POST /api/v1/auth/password/send-code

PasswordResetSendCodeResponseSerializer
인증 발송 응답

PasswordResetVerifyCodeSerializer
인증코드 확인
    POST /api/v1/auth/password/verify-code

PasswordResetVerifyCodeResponseSerializer
인증 확인 응답
"""


class PasswordResetSendCodeSerializer(serializers.Serializer[Any], BaseMixin):
    email = BaseMixin.get_email_field()


class PasswordResetSendCodeResponseSerializer(serializers.Serializer[Any]):

    message = serializers.CharField(default="인증 코드가 발송되었습니다.")
    expires_in = serializers.IntegerField(help_text="인증 코드 유효시간(초)")


class PasswordResetVerifyCodeSerializer(serializers.Serializer[Any], BaseMixin):
    email = BaseMixin.get_email_field()
    code = BaseMixin.get_email_code_field()

    def validate_code(self, value: str) -> str:
        return self.validate_email_code_format(value)


class PasswordResetVerifyCodeResponseSerializer(serializers.Serializer[Any]):
    verified = serializers.BooleanField(default=True)
    reset_token = serializers.CharField(
        help_text="비밀번호 재설정용 토큰 (10분 유효, 1회 사용)"
    )
    expires_in = serializers.IntegerField(help_text="토큰 유효시간(초)")


"""
비밀번호 재설정

PasswordResetSerializer
비밀번호 재설정
    POST /api/v1/auth/password/reset

PasswordResetResponseSerializer
비밀번호 재설정 응답
"""


class PasswordResetSerializer(serializers.Serializer[Any], BaseMixin):
    reset_token = BaseMixin.get_token_field(help_text="비밀번호 찾기 인증 후 받은 토큰")
    new_password = BaseMixin.get_password_field()
    new_password_confirm = BaseMixin.get_password_field()

    def validate_new_password(self, value: str) -> str:
        return self.validate_password_format(value)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # 비밀번호 일치 확인
        self.validate_password_match(
            attrs["new_password"], attrs["new_password_confirm"]
        )
        return attrs


class PasswordResetResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(default="비밀번호가 변경되었습니다.")
    changed_at = serializers.DateTimeField()


"""
비밀번호 변경 (로그인 상태)

PasswordChangeSerializer
비밀번호 변경 (로그인 상태)
    PUT /api/v1/users/me/password

"""


class PasswordChangeSerializer(serializers.Serializer[Any], BaseMixin):
    current_password = BaseMixin.get_password_field()
    new_password = BaseMixin.get_password_field()
    new_password_confirm = BaseMixin.get_password_field()

    def validate_new_password(self, value: str) -> str:
        return self.validate_password_format(value)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        self.validate_password_match(
            attrs["new_password"], attrs["new_password_confirm"]
        )
        return attrs


"""
비밀번호 변경 응답
"""


class PasswordChangeResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(default="비밀번호가 변경되었습니다.")
    changed_at = serializers.DateTimeField()
