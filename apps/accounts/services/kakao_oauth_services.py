from __future__ import annotations

from typing import Any

import requests
from django.conf import settings

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"


def exchange_code_for_token(*, code: str) -> Any:
    request = requests.post(
        KAKAO_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        },
        timeout=10,
    )
    request.raise_for_status()
    return request.json()


def fetch_userinfo(*, access_token: str) -> Any:
    request = requests.get(
        KAKAO_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    request.raise_for_status()
    return request.json()


def parse_profile(userinfo: dict[str, Any]) -> dict[str, str | None]:
    kakao_id = userinfo.get("id")
    account = userinfo.get("kakao_account") or {}
    profile = account.get("profile") or {}

    email = account.get("email")

    name = profile.get("name")
    picture = profile.get("profile_image_url")

    return {
        "provider_user_id": str(kakao_id) if kakao_id is not None else None,
        "email": email,
        "name": name,
        "picture": picture,
    }
