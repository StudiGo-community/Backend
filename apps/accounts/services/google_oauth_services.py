from __future__ import annotations

from typing import Any

import requests
from django.conf import settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def exchange_code_for_token(*, code: str) -> Any:
    request = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
            "code": code,
        },
        timeout=10,
    )
    request.raise_for_status()
    return request.json()


def fetch_userinfo(*, access_token: str) -> Any:
    request = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    request.raise_for_status()
    return request.json()


def parse_profile(userinfo: dict[str, Any]) -> dict[str, str | None]:
    return {
        "provider_user_id": str(userinfo.get("sub", "")) or None,
        "email": userinfo.get("email"),
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
    }
