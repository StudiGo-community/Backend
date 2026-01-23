from __future__ import annotations

import re
import secrets
from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
CACHE_KEY_PREFIX = "auth:signup:email-check:"


@dataclass(frozen=True)
class CheckEmailResult:
    message: str
    check_token: str | None = None
    expires_in: int | None = None


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _cache_key(email: str) -> str:
    return f"{CACHE_KEY_PREFIX}{email}"


def _ttl_seconds() -> int:
    return int(getattr(settings, "SIGNUP_EMAIL_CHECK_TTL", 60 * 5))


def validate_email_format(email: str) -> None:
    if not EMAIL_REGEX.match(email):
        raise ValueError("올바른 이메일 형식을 입력해주세요.")


def ensure_email_not_exists(email: str) -> None:
    User = get_user_model()
    if User.objects.filter(email=email).exists():
        raise ValueError("이미 가입된 이메일입니다.")


def issue_email_check_token(*, email: str) -> CheckEmailResult:
    """
    - 형식 검증
    - DB 중복 체크
    - Redis에 token 저장 (TTL)
    - token 반환
    """
    normalized = normalize_email(email)

    validate_email_format(normalized)
    ensure_email_not_exists(normalized)

    token = secrets.token_urlsafe(32)
    ttl = _ttl_seconds()

    # Redis 저장: key=email / value=token / TTL=ttl
    cache.set(_cache_key(normalized), token, timeout=ttl)

    return CheckEmailResult(
        message="사용 가능한 이메일입니다.",
        check_token=token,
        expires_in=ttl,
    )


def verify_email_check_token(
    *, email: str, check_token: str, consume: bool = True
) -> bool:
    """
    회원가입 단계에서 호출:
    - Redis에 저장된 token과 일치하면 True
    - consume=True면 1회성으로 삭제(재사용 방지)
    """
    normalized = normalize_email(email)
    key = _cache_key(normalized)

    cached = cache.get(key)
    if not cached:
        return False

    ok = secrets.compare_digest(str(cached), str(check_token))
    if ok and consume:
        cache.delete(key)
    return ok
