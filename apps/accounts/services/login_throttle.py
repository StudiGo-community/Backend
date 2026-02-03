from __future__ import annotations

import time
from dataclasses import dataclass

from django.core.cache import cache

from apps.core.security import (
    LOGIN_FAIL_BLOCK_COUNT_1,
    LOGIN_FAIL_BLOCK_COUNT_2,
    LOGIN_FAIL_BLOCK_TIME_1,
    LOGIN_FAIL_BLOCK_TIME_2,
    LOGIN_FAIL_COUNTER_TTL,
)

FAIL_KEY_PREFIX = "auth:login:fail:"
BLOCK_KEY_PREFIX = "auth:login:block:"


@dataclass(frozen=True)
class BlockState:
    is_blocked: bool
    retry_after_seconds: int


def _fail_key(email: str) -> str:
    return f"{FAIL_KEY_PREFIX}{email.lower().strip()}"


def _block_key(email: str) -> str:
    return f"{BLOCK_KEY_PREFIX}{email.lower().strip()}"


def check_blocked(email: str) -> BlockState:
    key = _block_key(email)
    until_ts = cache.get(key)
    if not until_ts:
        return BlockState(is_blocked=False, retry_after_seconds=0)

    now = int(time.time())
    retry = int(until_ts) - now
    if retry <= 0:
        cache.delete(key)
        cache.delete(_fail_key(email))  # 차단 풀리면 연속 실패도 초기화
        return BlockState(is_blocked=False, retry_after_seconds=0)

    return BlockState(is_blocked=True, retry_after_seconds=retry)


def record_login_failure(email: str) -> BlockState:
    # 이미 차단 중이면 그대로 반환
    blocked = check_blocked(email)
    if blocked.is_blocked:
        return blocked

    fkey = _fail_key(email)

    try:
        count = cache.incr(fkey)
    except ValueError:
        count = 1

    cache.set(fkey, count, timeout=LOGIN_FAIL_COUNTER_TTL)

    now = int(time.time())

    if count >= LOGIN_FAIL_BLOCK_COUNT_2:
        until = now + LOGIN_FAIL_BLOCK_TIME_2
        cache.set(_block_key(email), until, timeout=LOGIN_FAIL_BLOCK_TIME_2)
        return BlockState(is_blocked=True, retry_after_seconds=LOGIN_FAIL_BLOCK_TIME_2)

    if count >= LOGIN_FAIL_BLOCK_COUNT_1:
        until = now + LOGIN_FAIL_BLOCK_TIME_1
        cache.set(_block_key(email), until, timeout=LOGIN_FAIL_BLOCK_TIME_1)
        return BlockState(is_blocked=True, retry_after_seconds=LOGIN_FAIL_BLOCK_TIME_1)

    return BlockState(is_blocked=False, retry_after_seconds=0)


def clear_login_failures(email: str) -> None:
    cache.delete(_fail_key(email))
    cache.delete(_block_key(email))
