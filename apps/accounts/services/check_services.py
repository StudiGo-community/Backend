from __future__ import annotations

import secrets
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache


@dataclass(frozen=True)
class CheckResult:
    message: str
    check_token: str | None = None
    expires_in: int | None = None


def _ttl_seconds() -> int:
    return int(getattr(settings, "SIGNUP_CHECK_TTL", 60 * 5))


def _cache_key(prefix: str, value: str) -> str:
    return f"{prefix}{value}"


def _issue_token(*, prefix: str, value: str, message: str) -> CheckResult:
    token = secrets.token_urlsafe(32)
    ttl = _ttl_seconds()
    cache.set(_cache_key(prefix, value), token, timeout=ttl)
    return CheckResult(message=message, check_token=token, expires_in=ttl)


def _verify_token(
    *, prefix: str, value: str, check_token: str, consume: bool = True
) -> bool:
    key = _cache_key(prefix, value)
    cached = cache.get(key)
    if not cached:
        return False

    ok = secrets.compare_digest(str(cached), str(check_token))
    if ok and consume:
        cache.delete(key)
    return ok
