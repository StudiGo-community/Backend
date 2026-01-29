from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.cache import cache

from apps.core.security import OAUTH_STATE_TTL, SOCIAL_SIGNUP_SESSION_TTL


@dataclass(frozen=True)
class SocialSession:
    provider: str
    provider_user_id: str
    email: str | None = None
    name: str | None = None
    picture: str | None = None


def _ttl_state() -> int:
    return OAUTH_STATE_TTL


def _ttl_signup() -> int:
    return SOCIAL_SIGNUP_SESSION_TTL


def oauth_state_cache_key(provider: str, state: str) -> str:
    return f"oauth:state:{provider}:{state}"


def oauth_signup_session_cache_key(session_id: str) -> str:
    return f"oauth:signup:{session_id}"


def oauth_used_session_cache_key(session_id: str) -> str:
    return f"oauth:used:{session_id}"


def save_state(provider: str, state: str) -> None:
    cache.set(oauth_state_cache_key(provider, state), 1, timeout=_ttl_state())


def consume_state(provider: str, state: str) -> bool:
    key = oauth_state_cache_key(provider, state)
    if not cache.get(key):
        return False
    cache.delete(key)
    return True


def save_signup_session(session_id: str, data: SocialSession) -> None:
    cache.set(
        oauth_signup_session_cache_key(session_id),
        {
            "provider": data.provider,
            "provider_user_id": data.provider_user_id,
            "email": data.email,
            "name": data.name,
            "picture": data.picture,
        },
        timeout=_ttl_signup(),
    )


def load_signup_session(session_id: str) -> Any:
    return cache.get(oauth_signup_session_cache_key(session_id))


def mark_used_once(session_id: str) -> bool:
    # 이미 있으면 실패
    return bool(
        cache.add(oauth_used_session_cache_key(session_id), 1, timeout=_ttl_signup())
    )


def delete_signup_session(session_id: str) -> None:
    cache.delete(oauth_signup_session_cache_key(session_id))
