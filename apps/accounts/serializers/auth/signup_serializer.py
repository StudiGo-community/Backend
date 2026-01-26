from typing import Any, TypedDict

from rest_framework import serializers

from apps.accounts.models.users import User
from apps.accounts.serializers.base import BaseMixin
from apps.core.enumeration.account_user_enumeration import GenderChoices


class SignupUserOut(TypedDict):
    id: int
    email: str
    nickname: str
    created_at: str


"""
[회원가입]
SignupSerializer
이메일 회원가입 요청
    POST /api/v1/auth/signup

SignupResponseSerializer
회원가입 응답
"""


class SignupSerializer(serializers.Serializer[Any], BaseMixin):

    # 1. 인증 토큰 (View에서 서비스를 통해 검증)
    email_verification_token = BaseMixin.get_token_field()
    phone_verification_token = BaseMixin.get_token_field()

    # 2. 사용자 정보
    email = BaseMixin.get_email_field()
    password = BaseMixin.get_password_field()
    password_confirm = BaseMixin.get_password_field()
    nickname = BaseMixin.get_nickname_field()
    name = BaseMixin.get_name_field()
    gender = serializers.ChoiceField(choices=GenderChoices.choices)
    phone = BaseMixin.get_phone_field()
    birthday = serializers.DateField()

    # 3. 약관 동의
    terms_agreed = serializers.BooleanField()
    privacy_agreed = serializers.BooleanField()
    marketing_agreed = serializers.BooleanField(default=False, required=False)

    def validate_password(self, value: str) -> str:
        return self.validate_password_format(value)

    def validate_nickname(self, value: str) -> str:
        return self.validate_nickname_format(value)

    def validate_phone(self, value: str) -> str:
        return self.validate_phone_format(value)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # 비밀번호 일치 확인
        self.validate_password_match(attrs["password"], attrs["password_confirm"])

        # 약관 동의 검증
        if not attrs.get("terms_agreed"):
            raise serializers.ValidationError(
                {"terms_agreed": "이용약관에 동의해주세요."}
            )
        if not attrs.get("privacy_agreed"):
            raise serializers.ValidationError(
                {"privacy_agreed": "개인정보처리방침에 동의해주세요."}
            )

        return attrs


class SignupResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(default="회원가입이 완료되었습니다.")
    user = serializers.SerializerMethodField()

    def get_user(self, obj: User) -> SignupUserOut:
        return {
            "id": obj.id,
            "email": obj.email,
            "nickname": obj.nickname,
            "created_at": obj.created_at.isoformat(),
        }
