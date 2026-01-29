from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional, cast

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models.users import User
from apps.accounts.utils.cookies import (
    clear_access_cookie,
    clear_refresh_cookie,
)

ACCESS_LIFETIME = timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)

REFRESH_LIFETIME_DEFAULT = timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME)

REFRESH_LIFETIME_REMEMBER = timedelta(
    seconds=settings.JWT_REFRESH_TOKEN_LIFETIME_REMEMBERME
)


def authenticate_user(*, email: str, password: str) -> User | None:
    user = authenticate(email=email, password=password)
    return user


def issue_tokens(*, user: User, remember_me: bool) -> tuple[str, str, int]:
    refresh = RefreshToken.for_user(user)

    # access 1시간 고정
    access = refresh.access_token
    access.set_exp(lifetime=ACCESS_LIFETIME)

    # refresh: remember_me에 따라 24h / 30d
    refresh_lifetime = (
        REFRESH_LIFETIME_REMEMBER if remember_me else REFRESH_LIFETIME_DEFAULT
    )
    refresh.set_exp(lifetime=refresh_lifetime)

    refresh_max_age = int(refresh_lifetime.total_seconds())
    return str(access), str(refresh), refresh_max_age


def logout(*, request: Request, response: Response) -> Response:
    refresh_raw: Optional[str] = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)

    # 쿠키 제거
    clear_access_cookie(response)
    clear_refresh_cookie(response)

    # refresh 없으면 “이미 로그아웃”으로 성공 처리
    if not refresh_raw:
        return response

    # refresh blacklist
    token = RefreshToken(cast(Any, refresh_raw))
    token.blacklist()

    return response
