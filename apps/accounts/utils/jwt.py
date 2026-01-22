from __future__ import annotations

from typing import Literal, Optional, Tuple, cast

from rest_framework.request import Request
from rest_framework_simplejwt.settings import api_settings

SameSite = Optional[Literal["Lax", "Strict", "None", False]]


def coerce_samesite(value: object) -> SameSite:
    if value in ("Lax", "Strict", "None"):
        return cast(SameSite, value)
    return None


def is_jwt_like(token: str) -> bool:
    parts = token.split(".")
    return len(parts) == 3 and all(p for p in parts)


def extract_bearer_token(request: Request) -> Optional[str]:
    header_name = api_settings.AUTH_HEADER_NAME
    header_types = tuple(t.lower() for t in api_settings.AUTH_HEADER_TYPES)

    raw = request.META.get(header_name, "") or request.headers.get("Authorization", "")
    if not raw:
        return None

    parts: Tuple[str, str] | None = None
    try:
        scheme, token = raw.split(" ", 1)
        parts = (scheme.strip().lower(), token.strip())
    except ValueError:
        return None

    if parts and parts[0] in header_types and parts[1]:
        return parts[1]
    return None
