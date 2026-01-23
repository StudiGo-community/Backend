from __future__ import annotations

from typing import Any, Optional

from django.conf import settings
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieOrHeaderJWTAuthentication(JWTAuthentication):
    """
    - Authorization 헤더가 있으면 헤더 인증
    - 없으면 HttpOnly 쿠키의 access 토큰으로 인증
    """

    def authenticate(self, request: Request) -> Any:
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        cookie_name = getattr(settings, "AUTH_ACCESS_COOKIE_NAME", "access")
        raw_token: Optional[str] = request.COOKIES.get(cookie_name)
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return (user, validated_token)
