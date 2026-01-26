from __future__ import annotations

import hmac
import time
import uuid
from typing import Any, Optional

import jwt
from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed

REDIS_JTI_PREFIX = "verify:jti"
REDIS_USED_PREFIX = "verify:used"


def _serialize_purpose(purpose: Any) -> str:
    return getattr(purpose, "value", str(purpose))


def _jti_key(purpose: str, jti: str) -> str:
    return f"{REDIS_JTI_PREFIX}:{purpose}:{jti}"


def _used_key(jti: str) -> str:
    return f"{REDIS_USED_PREFIX}:{jti}"


def _strip_bearer(token: str) -> str:
    t = token.strip()
    return t[7:].strip() if t.lower().startswith("bearer ") else t


def _safe_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(str(a), str(b))


def _now() -> int:
    return int(time.time())


def issue_verify_token(*, sub: str, purpose: Any) -> str:
    ttl = int(getattr(settings, "VERIFY_TOKEN_EXPIRES_SECONDS", 600))
    algo = getattr(settings, "VERIFY_TOKEN_ALGO", "HS256")
    secret = getattr(settings, "SECRET_KEY", None)
    purpose = _serialize_purpose(purpose)
    if not secret:
        raise RuntimeError("SECRET_KEY is not set")

    now = _now()
    jti = uuid.uuid4().hex
    exp = now + ttl

    claims = {
        "sub": sub,
        "purpose": purpose,
        "jti": jti,
        "iat": now,
        "exp": exp,
    }
    token = jwt.encode(claims, secret, algorithm=algo)
    cache.set(_jti_key(purpose, jti), 1, timeout=ttl)
    return token


def verify_and_consume(
    token: str,
    *,
    expected_purpose: Any,
    expected_sub: Optional[str] = None,
) -> dict[str, Any]:
    algo = getattr(settings, "VERIFY_TOKEN_ALGO", "HS256")
    secret = getattr(settings, "SECRET_KEY", None)
    if not secret:
        raise RuntimeError("SECRET_KEY is not set")

    raw = _strip_bearer(token)

    try:
        decoded: dict[str, Any] = jwt.decode(raw, secret, algorithms=[algo])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise AuthenticationFailed(
            {"detail": "검증 토큰이 유효하지 않거나 만료되었습니다."}
        )

    purpose = _serialize_purpose(decoded.get("purpose"))
    sub = str(decoded.get("sub", ""))
    jti = str(decoded.get("jti", ""))

    if not _safe_eq(purpose, _serialize_purpose(expected_purpose)):
        raise AuthenticationFailed(
            {"detail": "검증 토큰이 유효하지 않거나 만료되었습니다."}
        )

    if expected_sub is not None and not _safe_eq(sub, expected_sub):
        raise AuthenticationFailed(
            {"detail": "검증 토큰이 유효하지 않거나 만료되었습니다."}
        )

    jti_key = _jti_key(purpose, jti)
    if not cache.get(jti_key):
        raise AuthenticationFailed(
            {"detail": "검증 토큰이 유효하지 않거나 만료되었습니다."}
        )

    # 재사용 방지(짧게만 막아도 충분)
    if not cache.add(_used_key(jti), 1, timeout=60):
        raise AuthenticationFailed(
            {"detail": "검증 토큰이 유효하지 않거나 만료되었습니다."}
        )

    cache.delete(jti_key)
    return decoded
