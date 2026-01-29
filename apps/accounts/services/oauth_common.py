from __future__ import annotations

import re
from typing import Any

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

PHONE_RE = re.compile(r"\D+")


def normalize_phone(phone: str) -> str:
    # 숫자만 남기기 (ex: 010-1234-5678 -> 01012345678)
    return PHONE_RE.sub("", phone or "").strip()


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
