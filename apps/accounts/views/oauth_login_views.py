from __future__ import annotations

import secrets

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.utils.session_cache import save_state

ALLOWED_PURPOSE = {"login", "withdrawal"}


def _get_purpose(request: Request) -> str:
    purpose = (request.query_params.get("purpose") or "login").strip().lower()
    return purpose if purpose in ALLOWED_PURPOSE else "login"


class GoogleLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["유저"],
        operation_id="oauth_google_login",
        summary="소셜 로그인 시작 - 구글",
        description=(
            "스웨거로 테스트 불가" "/api/v1/oauth/google/login/ 접속해 테스트"
        ),
    )
    def get(self, request: Request) -> HttpResponse:
        purpose = _get_purpose(request)
        nonce = secrets.token_urlsafe(24)

        state = f"{purpose}:{nonce}"
        save_state("google", state)

        scope = "openid email profile"
        url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope={scope.replace(' ', '%20')}"
            f"&state={state}"
        )
        return redirect(url)


class KakaoLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["유저"],
        operation_id="oauth_kakao_login",
        summary="소셜 로그인 시작 - 카카오",
        description=("스웨거로 테스트 불가" "/api/v1/oauth/kakao/login/ 접속해 테스트"),
    )
    def get(self, request: Request) -> HttpResponse:
        purpose = _get_purpose(request)
        nonce = secrets.token_urlsafe(24)

        state = f"{purpose}:{nonce}"
        save_state("kakao", state)

        scope = "account_email profile_nickname profile_image"
        url = (
            "https://kauth.kakao.com/oauth/authorize"
            f"?client_id={settings.KAKAO_CLIENT_ID}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope={scope.replace(' ', '%20')}"
            f"&state={state}"
        )
        return redirect(url)
