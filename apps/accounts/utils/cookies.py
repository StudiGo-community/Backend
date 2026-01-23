from __future__ import annotations

from typing import Literal, Optional, cast

from django.conf import settings
from rest_framework.response import Response

CookieType = Literal["access", "refresh"]
SameSite = Optional[Literal["Lax", "Strict", "None", False]]


def _cookie_samesite(type: CookieType) -> SameSite:
    # access/refresh 각각의 samesite 설정을 읽도록 분리
    attr = (
        "AUTH_ACCESS_COOKIE_SAMESITE"
        if type == "access"
        else "AUTH_REFRESH_COOKIE_SAMESITE"
    )
    value = getattr(settings, attr, None)
    if value in ("Lax", "Strict", "None", False):
        return cast(SameSite, value)
    return None


def _cookie_attr(type: CookieType, suffix: str) -> str:
    # settings 속성명 생성
    prefix = "AUTH_ACCESS_COOKIE_" if type == "access" else "AUTH_REFRESH_COOKIE_"
    return f"{prefix}{suffix}"


def _get(type: CookieType, suffix: str) -> object:
    return getattr(settings, _cookie_attr(type, suffix))


def _set_cookie(
    response: Response, *, type: CookieType, token: str, max_age: int
) -> None:
    response.set_cookie(
        key=cast(str, _get(type, "NAME")),
        value=token,
        max_age=max_age,
        path=cast(str, _get(type, "PATH")),
        secure=cast(bool, _get(type, "SECURE")),
        httponly=cast(bool, _get(type, "HTTPONLY")),
        samesite=_cookie_samesite(type),
    )


def _clear_cookie(response: Response, *, type: CookieType) -> None:
    response.delete_cookie(
        key=cast(str, _get(type, "NAME")),
        path=cast(str, _get(type, "PATH")),
        samesite=_cookie_samesite(type),
    )


def set_access_cookie(response: Response, access: str, *, max_age: int) -> None:
    _set_cookie(response, type="access", token=access, max_age=max_age)


def clear_access_cookie(response: Response) -> None:
    _clear_cookie(response, type="access")


def set_refresh_cookie(response: Response, refresh: str, *, max_age: int) -> None:
    _set_cookie(response, type="refresh", token=refresh, max_age=max_age)


def clear_refresh_cookie(response: Response) -> None:
    _clear_cookie(response, type="refresh")
