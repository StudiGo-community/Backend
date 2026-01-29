from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.services.google_oauth_services import (
    exchange_code_for_token as google_exchange,
)
from apps.accounts.services.google_oauth_services import (
    fetch_userinfo as google_userinfo,
)
from apps.accounts.services.google_oauth_services import parse_profile as google_parse
from apps.accounts.services.kakao_oauth_services import (
    exchange_code_for_token as kakao_exchange,
)
from apps.accounts.services.kakao_oauth_services import fetch_userinfo as kakao_userinfo
from apps.accounts.services.kakao_oauth_services import parse_profile as kakao_parse
from apps.accounts.utils.session_cache import consume_state

from .oauth_handler import handle_social_callback


class GoogleCallbackView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["유저"],
        operation_id="oauth_google_callback",
        summary="소셜 로그인 콜백 - 구글",
        description=(
            "스웨거로 테스트 불가" "/api/v1/oauth/google/login/ API 실행 후 리다이렉트"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "session_id": {"type": "string"},
                },
            }
        },
    )
    def get(self, request: Request) -> Response:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not code or not state:
            raise ValidationError({"detail": "요청값이 올바르지 않습니다."})

        if not consume_state("google", state):
            raise AuthenticationFailed({"detail": "유효하지 않은 요청입니다."})

        try:
            token = google_exchange(code=code)
            userinfo = google_userinfo(access_token=token["access_token"])
        except Exception:
            raise AuthenticationFailed({"detail": "소셜 인증 처리에 실패했습니다."})

        profile = google_parse(userinfo)

        return handle_social_callback(
            provider="google",
            provider_user_id=profile.get("provider_user_id"),
            email=profile.get("email"),
            name=profile.get("name"),
            picture=profile.get("picture"),
        )


class KakaoCallbackView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["유저"],
        operation_id="oauth_kakao_callback",
        summary="소셜 로그인 콜백 - 카카오",
        description=(
            "스웨거로 테스트 불가" "/api/v1/oauth/kakao/login/ API 실행 후 리다이렉트"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "session_id": {"type": "string"},
                },
            }
        },
    )
    def get(self, request: Request) -> Response:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not code or not state:
            raise ValidationError({"detail": "요청값이 올바르지 않습니다."})

        if not consume_state("kakao", state):
            raise AuthenticationFailed({"detail": "유효하지 않은 요청입니다."})

        try:
            token = kakao_exchange(code=code)
            userinfo = kakao_userinfo(access_token=token["access_token"])
        except Exception:
            raise AuthenticationFailed({"detail": "소셜 인증 처리에 실패했습니다."})

        profile = kakao_parse(userinfo)

        return handle_social_callback(
            provider="kakao",
            provider_user_id=profile.get("provider_user_id"),
            email=profile.get("email"),
            name=profile.get("name"),
            picture=profile.get("picture"),
        )
