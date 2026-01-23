from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional, cast

from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers.auth_serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    TokenPayloadSerializer,
)
from apps.accounts.services.auth_services import authenticate_user, issue_tokens
from apps.accounts.services.login_throttle import (
    check_blocked,
    clear_login_failures,
    record_login_failure,
)
from apps.accounts.utils.cookies import (
    clear_access_cookie,
    clear_refresh_cookie,
    set_access_cookie,
    set_refresh_cookie,
)
from apps.core.enumeration.account_user_enumeration import UserStatus

ACCESS_LIFETIME = timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)
expires_in = int(ACCESS_LIFETIME.total_seconds())


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: tuple[Any, ...] = ()

    @extend_schema(
        tags=["유저"],
        operation_id="auth_login",
        summary="이메일 로그인",
        description=(
            "이메일과 비밀번호로 로그인합니다.\n\n"
            "- Access Token은 응답 body로 반환됩니다.\n"
            "- Refresh Token은 HttpOnly 쿠키로 저장됩니다.\n"
            "- remember_me=true인 경우 Refresh Token 만료기간이 30일로 연장됩니다."
        ),
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            429: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request: Request) -> Response:
        in_ser = LoginRequestSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        email: str = in_ser.validated_data["email"].strip().lower()
        password: str = in_ser.validated_data["password"]
        remember_me: bool = in_ser.validated_data.get("remember_me", False)

        # 연속 실패 차단 체크 (email 기준)
        blocked = check_blocked(email)
        if blocked.is_blocked:
            return Response(
                {
                    "detail": f"로그인 시도가 제한되었습니다. {blocked.retry_after_seconds}초 후 다시 시도해주세요."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 인증
        user = authenticate_user(email=email, password=password)
        if user is None:
            # 실패 누적/차단
            new_block = record_login_failure(email)
            if new_block.is_blocked:
                return Response(
                    {
                        "detail": "로그인 시도가 제한되었습니다. 잠시 후 다시 시도해주세요."
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            return Response(
                {"detail": "이메일 또는 비밀번호를 확인해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 상태/활성 체크
        if not user.is_active:
            return Response(
                {"detail": "비활성화된 계정입니다."}, status=status.HTTP_403_FORBIDDEN
            )

        if user.status != UserStatus.ACTIVE:
            if user.status == UserStatus.BANNED:
                return Response(
                    {"detail": "이용이 제한된 계정입니다."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if user.status == UserStatus.DORMANT:
                return Response(
                    {"detail": "휴면 계정입니다."}, status=status.HTTP_403_FORBIDDEN
                )
            if user.status == UserStatus.DEACTIVATED:
                return Response(
                    {"detail": "비활성화된 계정입니다."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                {"detail": "로그인할 수 없는 계정 상태입니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 실패 카운트 초기화
        clear_login_failures(email)

        # 토큰 발급 + refresh 쿠키 저장
        access, refresh, refresh_max_age = issue_tokens(
            user=user, remember_me=remember_me
        )

        out = LoginResponseSerializer(
            {
                "token": {
                    "access_token": access,
                    "token_type": "Bearer",
                    "expires_in": expires_in,
                },
                "user": user,
            }
        )

        response = Response(
            {"detail": "로그인 되었습니다.", "data": out.data},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, refresh, max_age=refresh_max_age)
        set_access_cookie(response, access, max_age=expires_in)
        return response


class TokenRefreshAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_token_refresh",
        summary="토큰 갱신",
        description="HttpOnly 쿠키의 Refresh Token으로 Access Token을 재발급합니다.",
        request=None,
        responses={200: TokenPayloadSerializer},
    )
    def post(self, request: Request) -> Response:
        refresh_raw: Optional[str] = request.COOKIES.get(
            settings.AUTH_REFRESH_COOKIE_NAME
        )
        if not refresh_raw:
            return Response(
                {"detail": "리프레시 토큰이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(cast(Any, refresh_raw))
            access = str(refresh.access_token)
        except TokenError:
            return Response(
                {"detail": "유효하지 않은 리프레시 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        out = TokenPayloadSerializer(
            instance={
                "access_token": access,
                "token_type": "Bearer",
                "expires_in": expires_in,
            }
        )
        resp = Response(out.data, status=status.HTTP_200_OK)
        set_access_cookie(resp, access, max_age=expires_in)
        return resp


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_logout",
        summary="로그아웃",
        description="Refresh Token을 무효화(blacklist)하고 쿠키를 삭제합니다.",
        request=None,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "로그아웃되었습니다."}
                },
            }
        },
    )
    def post(self, request: Request) -> Response:
        refresh_raw: Optional[str] = request.COOKIES.get(
            settings.AUTH_REFRESH_COOKIE_NAME
        )

        # 응답은 항상 쿠키 삭제
        response = Response(
            {"detail": "로그아웃되었습니다."}, status=status.HTTP_200_OK
        )
        clear_refresh_cookie(response)
        clear_access_cookie(response)

        # refresh 없으면 “이미 로그아웃”으로 성공 처리
        if not refresh_raw:
            return response

        # blacklist 가능하면 시도 (token_blacklist 앱이 켜져있어야 정상 동작)
        try:
            token = RefreshToken(cast(Any, refresh_raw))
            token.blacklist()
        except Exception:
            # 만료/위조/이미 블랙리스트 등은 그냥 성공 처리
            return response

        return response
