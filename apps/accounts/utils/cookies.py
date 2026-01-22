from __future__ import annotations

from typing import Literal, Optional, cast

from django.conf import settings
from rest_framework.response import Response

SameSite = Optional[Literal["Lax", "Strict", "None", False]]


def _cookie_samesite() -> SameSite:
    value = getattr(settings, "AUTH_REFRESH_COOKIE_SAMESITE", None)
    if value in ("Lax", "Strict", "None"):
        return cast(SameSite, value)
    return None


def set_refresh_cookie(response: Response, refresh: str, *, max_age: int) -> None:
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh,
        max_age=max_age,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        httponly=settings.AUTH_REFRESH_COOKIE_HTTPONLY,
        samesite=_cookie_samesite(),
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        samesite=_cookie_samesite(),
    )
