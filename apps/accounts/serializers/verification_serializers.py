from typing import Any

from rest_framework import serializers

from apps.accounts.models.users import User
from apps.accounts.serializers.base import BaseMixin
from apps.core.enumeration.account_verification_enumeration import (
    EmailVerificationPurpose,
    PhoneVerificationPurpose,
)

"""
이메일/휴대폰 인증 코드 발송 및 확인
-[이메일 인증]: 인증코드 발송 요청/확인 요청 및 응답
-[휴대폰 인증]: 인증코드 발송 요청/확인 요청 및 응답
"""

"""
EmailSendCodeSerializer
이메일 인증코드 발송 요청
    POST /api/v1/auth/email/send-code

EmailVerifyCodeSerializer
이메일 인증코드 확인 요청
    POST /api/v1/auth/email/verify-code

EmailVerifyResponseSerializer
    이메일 인증 확인 응답
"""


class EmailSendCodeSerializer(serializers.Serializer[Any], BaseMixin):
    email = BaseMixin.get_email_field()
    purpose = serializers.ChoiceField(
        choices=EmailVerificationPurpose.choices,
        default=EmailVerificationPurpose.SIGNUP,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs["email"]
        purpose = attrs["purpose"]

        user_exists = User.objects.filter(email=email).exists()

        if purpose == EmailVerificationPurpose.SIGNUP:
            if user_exists:
                raise serializers.ValidationError(
                    {"email": "이미 가입된 이메일입니다."}
                )

        elif purpose == EmailVerificationPurpose.PASSWORD_RESET:
            if not user_exists:
                raise serializers.ValidationError(
                    {"email": "가입되지 않은 이메일입니다."}
                )
            user = User.objects.get(email=email)
            # 소셜 전용 계정 체크 (password가 비어있거나 unusable이면 소셜 전용)
            if not user.has_usable_password():
                raise serializers.ValidationError(
                    {
                        "email": "소셜 로그인 계정입니다. 해당 소셜 서비스로 로그인해주세요."
                    }
                )

        else:
            raise serializers.ValidationError({"email": "존재하지 않는 계정입니다."})

        return attrs


class EmailVerifyCodeSerializer(serializers.Serializer[Any], BaseMixin):
    email = BaseMixin.get_email_field()
    code = BaseMixin.get_email_code_field()
    purpose = serializers.ChoiceField(
        choices=EmailVerificationPurpose.choices,
        default=EmailVerificationPurpose.SIGNUP,
    )

    def validate_code(self, value: str) -> str:
        return self.validate_email_code_format(value)


class EmailVerifyResponseSerializer(serializers.Serializer[Any]):
    verified = serializers.BooleanField()
    verification_token = serializers.CharField(
        help_text="회원가입/비밀번호 재설정 시 사용할 토큰"
    )
    expires_in = serializers.IntegerField(help_text="토큰 유효시간(초)")


"""
[휴대폰 인증번호]
PhoneSendCodeSerializer
휴대폰 인증번호 발송 요청
    POST /api/v1/auth/phone/send-code

PhoneVerifyCodeSerializer
휴대폰 인증번호 확인 요청
    POST /api/v1/auth/phone/verify-code

PhoneVerifyResponseSerializer(serializers.Serializer):
휴대폰 인증 확인 응답
"""


class PhoneSendCodeSerializer(serializers.Serializer[Any], BaseMixin):
    phone = BaseMixin.get_phone_field()
    purpose = serializers.ChoiceField(
        choices=PhoneVerificationPurpose.choices,
        default=PhoneVerificationPurpose.SIGNUP,
    )

    def validate_phone(self, value: str) -> str:
        return self.validate_phone_format(value)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        phone = attrs["phone"]
        purpose = attrs["purpose"]

        user_exists = User.objects.filter(phone=phone).exists()

        if purpose == PhoneVerificationPurpose.SIGNUP:
            if user_exists:
                raise serializers.ValidationError(
                    {"phone": "이미 가입된 휴대폰 번호입니다."}
                )

        elif purpose == PhoneVerificationPurpose.EMAIL_FINDING:
            if not user_exists:
                raise serializers.ValidationError(
                    {"phone": "가입되지 않은 휴대폰 번호입니다."}
                )

        return attrs


class PhoneVerifyCodeSerializer(serializers.Serializer[Any], BaseMixin):
    phone = BaseMixin.get_phone_field()
    code = BaseMixin.get_phone_code_field()
    purpose = serializers.ChoiceField(
        choices=PhoneVerificationPurpose.choices,
        default=PhoneVerificationPurpose.SIGNUP,
    )

    def validate_phone(self, value: str) -> str:
        return self.validate_phone_format(value)

    def validate_code(self, value: str) -> str:
        return self.validate_phone_code_format(value)


class PhoneVerifyResponseSerializer(serializers.Serializer[Any]):
    verified = serializers.BooleanField()
    verification_token = serializers.CharField(help_text="회원가입 시 사용할 토큰")
    expires_in = serializers.IntegerField(help_text="토큰 유효시간(초)")
