from typing import Any

from rest_framework import serializers

from apps.accounts.models.users import OAuthAccount, User
from apps.accounts.serializers.base import BaseMixin
from apps.core.enumeration.account_user_enumeration import (
    GenderChoices,
    SocialProviderChoices,
)

"""
소셜 로그인 (카카오, 구글)

-[OAuth 요청]
-[OAuth 응답]
-[소셜 프로필 파싱]
-[소셜 추가정보 입력]
"""

"""
[OAuth 요청]
KakaoOAuthSerializer
카카오 OAuth 요청
    POST /api/v1/auth/oauth/kakao

GoogleOAuthSerializer
구글 OAuth 요청
    POST /api/v1/auth/oauth/google
"""


class KakaoOAuthSerializer(serializers.Serializer[Any]):
    authorization_code = serializers.CharField(help_text="카카오 인가 코드")
    redirect_uri = serializers.URLField(help_text="리다이렉트 URI")


class GoogleOAuthSerializer(serializers.Serializer[Any]):
    authorization_code = serializers.CharField(help_text="구글 인가 코드")
    redirect_uri = serializers.URLField(help_text="리다이렉트 URI")


"""
[OAuth 응답]
OAuthResponseSerializer
OAuth 응답 (기존 회원 / 신규 회원 분기)
    - 기존 회원: 바로 로그인 (access_token, refresh_token 반환)
    - 신규 회원: 추가정보 입력 필요 (temporary_token 반환)
"""


class OAuthResponseSerializer(serializers.Serializer[Any]):
    is_new_user = serializers.BooleanField(help_text="신규 사용자 여부")
    requires_additional_info = serializers.BooleanField(
        help_text="추가정보 입력 필요 여부"
    )

    # 신규 회원 - 추가정보 입력 필요
    temporary_token = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="추가정보 입력 시 사용할 임시 토큰 (15분 유효)",
    )

    # 기존 회원 - 바로 로그인
    access_token = serializers.CharField(required=False, allow_null=True)
    refresh_token = serializers.CharField(required=False, allow_null=True)
    token_type = serializers.CharField(default="Bearer", required=False)
    expires_in = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Access Token 만료시간(초)",
    )
    user = serializers.DictField(required=False, allow_null=True)


"""
[소셜 프로필 파싱]
KakaoProfileSerializer
카카오 프로필 파싱용 (내부 사용)

GoogleProfileSerializer
구글 프로필 파싱용 (내부 사용)
"""


class KakaoProfileSerializer(serializers.Serializer[Any]):
    id = serializers.CharField()
    kakao_account = serializers.DictField()

    def validate(self, attrs: Any) -> dict[str, Any]:
        kakao_account = attrs.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        # 필수 정보 검증
        if "email" not in kakao_account:
            raise serializers.ValidationError(
                {
                    "email": "카카오 계정에서 이메일 정보를 가져올 수 없습니다. 이메일 제공에 동의해주세요."
                }
            )

        return {
            "provider": SocialProviderChoices.K,
            "provider_user_id": str(attrs["id"]),
            "email": kakao_account.get("email"),
            "name": profile.get("nickname"),
            "profile_image": profile.get("profile_image_url"),
        }


class GoogleProfileSerializer(serializers.Serializer[Any]):
    sub = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField(required=False, allow_blank=True)
    picture = serializers.URLField(required=False, allow_blank=True)

    def validate(self, attrs: Any) -> dict[str, Any]:
        return {
            "provider": SocialProviderChoices.G,
            "provider_user_id": attrs["sub"],
            "email": attrs["email"],
            "name": attrs.get("name"),
            "profile_image": attrs.get("picture"),
        }


"""
[소셜 추가정보 입력]
SocialSignupCompleteSerializer
소셜 로그인 추가정보 입력
    POST /api/v1/auth/oauth/complete-signup

SocialSignupCompleteResponseSerializer
소셜 회원가입 완료 응답
"""


class SocialSignupCompleteSerializer(serializers.Serializer[Any], BaseMixin):
    # 임시 토큰 (OAuth에서 발급, 15분 유효, View에서 검증)
    temporary_token = BaseMixin.get_token_field()

    # 추가 정보
    nickname = BaseMixin.get_nickname_field()
    name = BaseMixin.get_name_field(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=GenderChoices.choices)
    phone = BaseMixin.get_phone_field()
    phone_verification_token = BaseMixin.get_token_field(
        help_text="휴대폰 인증 완료 후 받은 토큰"
    )
    birthday = serializers.DateField()

    # 약관 동의
    terms_agreed = serializers.BooleanField()
    privacy_agreed = serializers.BooleanField()
    marketing_agreed = serializers.BooleanField(default=False, required=False)

    def validate_nickname(self, value: str) -> str:
        value = self.validate_nickname_format(value)
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def validate_phone(self, value: str) -> str:
        value = self.validate_phone_format(value)
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("이미 가입된 휴대폰 번호입니다.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
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

    def create(self, validated_data: dict[str, Any]) -> User:
        # check one more time
        social_data = self.context.get("social_data")
        if not social_data:
            raise serializers.ValidationError({"detail": "소셜 인증 정보가 없습니다."})

        # 불필요한 필드 제거
        validated_data.pop("temporary_token")
        validated_data.pop("phone_verification_token")
        validated_data.pop("terms_agreed")
        validated_data.pop("privacy_agreed")
        validated_data.pop("marketing_agreed", None)

        # UserManager.create_user() 사용 (비밀번호 없음 - 소셜 로그인 전용)
        user = User.objects.create_user(
            email=social_data["email"],
            password=None,  # 소셜 로그인은 비밀번호 없음
            nickname=validated_data["nickname"],
            name=validated_data.get("name") or social_data.get("name", ""),
            gender=validated_data["gender"],
            phone=validated_data["phone"],
            birthday=validated_data["birthday"],
            profile_image_url=social_data.get("profile_image"),
            is_active=True,  # 회원가입 완료 시 활성화
        )

        # OAuthAccount 생성
        OAuthAccount.objects.create(
            user=user,
            provider=social_data["provider"],
            provider_user_id=social_data["provider_user_id"],
            social_email=social_data["email"],
            access_token=social_data.get("access_token", ""),
            refresh_token=social_data.get("refresh_token", ""),
        )

        return user


class SocialSignupCompleteResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(default="회원가입이 완료되었습니다.")
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")
    expires_in = serializers.IntegerField(help_text="Access Token 만료시간(초)")
    user = serializers.DictField()
