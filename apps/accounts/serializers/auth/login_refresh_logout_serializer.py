from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers.auth.auth_common import (
    Any,
    BaseMixin,
    TypedDict,
    User,
    serializers,
)
from apps.core.enumeration.account_user_enumeration import UserStatus

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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs["email"]
        password = attrs["password"]

        # 사용자 조회
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "이메일 또는 비밀번호를 확인해주세요."}
            )

        # 비밀번호 검증
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "이메일 또는 비밀번호를 확인해주세요."}
            )

        # 계정 활성화 여부 확인
        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "detail": "비활성화된 계정입니다. 관리자에게 문의하세요.",
                    "error_code": "ACCOUNT_INACTIVE",
                }
            )

        # 계정 상태 검증
        if user.status == UserStatus.DEACTIVATED:
            raise serializers.ValidationError(
                {
                    "detail": "탈퇴한 계정입니다. 30일 이내 복구 가능합니다.",
                    "error_code": "ACCOUNT_DEACTIVATED",
                    "can_restore": "true",
                }
            )
        elif user.status == UserStatus.BANNED:
            raise serializers.ValidationError(
                {
                    "detail": "정지된 계정입니다.",
                    "error_code": "ACCOUNT_BANNED",
                }
            )
        elif user.status == UserStatus.DORMANT:
            raise serializers.ValidationError(
                {
                    "detail": "휴면 계정입니다. 휴면 해제 후 이용해주세요.",
                    "error_code": "ACCOUNT_DORMANT",
                }
            )

        attrs["user"] = user
        return attrs


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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            token = RefreshToken(attrs["refresh_token"])
            attrs["access_token"] = str(token.access_token)
            attrs["refresh_token_instance"] = token
        except TokenError:
            raise serializers.ValidationError(
                {"refresh_token": "유효하지 않거나 만료된 토큰입니다."}
            )
        return attrs


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
    all_devices = serializers.BooleanField(
        default=False,
        required=False,
        help_text="True면 모든 기기에서 로그아웃",
    )


class LogoutResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(default="로그아웃되었습니다.")
