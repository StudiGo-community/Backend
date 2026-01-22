from __future__ import annotations

import time
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache

FAIL_KEY_PREFIX = "auth:login:fail:"
BLOCK_KEY_PREFIX = "auth:login:block:"

FAIL_LIMIT_1 = settings.LOGIN_FAIL_BLOCK_COUNT_1
FAIL_LIMIT_2 = settings.LOGIN_FAIL_BLOCK_COUNT_2

BLOCK_TIME_1 = settings.LOGIN_FAIL_BLOCK_TIME_1
BLOCK_TIME_2 = settings.LOGIN_FAIL_BLOCK_TIME_2

FAIL_COUNTER_TTL = settings.LOGIN_FAIL_COUNTER_TTL


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

    cache.set(fkey, count, timeout=FAIL_COUNTER_TTL)

    now = int(time.time())

    if count >= FAIL_LIMIT_2:
        until = now + BLOCK_TIME_2
        cache.set(_block_key(email), until, timeout=BLOCK_TIME_2)
        return BlockState(is_blocked=True, retry_after_seconds=BLOCK_TIME_2)

    if count >= FAIL_LIMIT_1:
        until = now + BLOCK_TIME_1
        cache.set(_block_key(email), until, timeout=BLOCK_TIME_1)
        return BlockState(is_blocked=True, retry_after_seconds=BLOCK_TIME_1)

    return BlockState(is_blocked=False, retry_after_seconds=0)


def clear_login_failures(email: str) -> None:
    cache.delete(_fail_key(email))
    cache.delete(_block_key(email))
