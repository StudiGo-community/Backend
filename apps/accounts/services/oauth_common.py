from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


def ensure_phone_not_exists(phone: str) -> None:
    User = get_user_model()
    if User.objects.filter(phone=phone).exists():
        raise ValueError("이미 등록된 휴대폰 번호입니다.")


def issue_jwt_for_user(user: Any) -> dict[str, Any]:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "access_expires_in": int(refresh.access_token.lifetime.total_seconds()),
        "refresh_expires_in": int(refresh.lifetime.total_seconds()),
    }
