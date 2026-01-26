from typing import Any, TypedDict

from rest_framework import serializers

from apps.accounts.models.users import User
from apps.accounts.serializers.base import BaseMixin

"""
[로그인/토큰갱신/로그아웃]
- 시리얼라이저: 입력 형식 검증만
- 서비스: 사용자 인증, 토큰 발급/검증/블랙리스트 관리

LoginSerializer
로그인 요청
    POST /api/v1/auth/login

TokenRefreshSerializer
토큰 갱신 요청
    POST /api/v1/auth/refresh

LogoutSerializer
로그아웃 요청
    POST /api/v1/auth/logout
"""


"""
[로그인]
LoginSerializer
로그인 요청
    POST /api/v1/auth/login

LoginResponseSerializer
로그인 응답
"""


class LoginResponseContext(TypedDict):
    user: User


class LoginUserOut(TypedDict):
    id: int
    email: str
    nickname: str
    name: str
    profile_image_url: str | None
    role: str


class LoginSerializer(serializers.Serializer[Any], BaseMixin):
    email = BaseMixin.get_email_field()
    password = BaseMixin.get_password_field()
    remember_me = serializers.BooleanField(default=False, required=False)


class LoginResponseSerializer(serializers.Serializer[Any]):

    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")
    expires_in = serializers.IntegerField(help_text="Access Token 만료시간(초)")
    user = serializers.SerializerMethodField()

    def get_user(self, obj: LoginResponseContext) -> LoginUserOut:
        user = obj.get("user")
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "name": user.name,
            "profile_image_url": user.profile_image_url,
            "role": user.role,
        }


"""
토큰 갱신

TokenRefreshSerializer
토큰 갱신 요청
    POST /api/v1/auth/refresh

TokenRefreshResponseSerializer
토큰 갱신 응답
"""


class TokenRefreshSerializer(serializers.Serializer[Any]):
    refresh_token = serializers.CharField()


class TokenRefreshResponseSerializer(serializers.Serializer[Any]):
    access_token = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")
    expires_in = serializers.IntegerField(help_text="Access Token 만료시간(초)")


"""
[로그아웃]
LogoutSerializer
로그아웃 요청
    POST /api/v1/auth/logout

LogoutResponseSerializer
로그아웃 응답
"""


class LogoutSerializer(serializers.Serializer[Any]):
    refresh_token = serializers.CharField(required=False, allow_blank=True)


class LogoutResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(default="로그아웃되었습니다.")
