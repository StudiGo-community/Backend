from __future__ import annotations

import re

from django.contrib.auth import get_user_model

from apps.accounts.services.check_services import (
    CheckResult,
    _issue_token,
    _verify_token,
)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

EMAIL_PREFIX = "auth:signup:email-check:"


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_email_format(email: str) -> None:
    if not EMAIL_REGEX.match(email):
        raise ValueError("올바른 이메일 형식을 입력해주세요.")


def ensure_email_not_exists(email: str) -> None:
    User = get_user_model()
    if User.objects.filter(email=email).exists():
        raise ValueError("이미 가입된 이메일입니다.")


def issue_email_check_token(*, email: str) -> CheckResult:
    value = normalize_email(email)
    validate_email_format(value)
    ensure_email_not_exists(value)
    return _issue_token(
        prefix=EMAIL_PREFIX, value=value, message="사용 가능한 이메일입니다."
    )


def verify_email_check_token(
    *, email: str, check_token: str, consume: bool = True
) -> bool:
    value = normalize_email(email)
    return _verify_token(
        prefix=EMAIL_PREFIX, value=value, check_token=check_token, consume=consume
    )
