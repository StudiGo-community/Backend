from django.contrib.auth import get_user_model

from apps.accounts.services.check_services import (
    CheckResult,
    _issue_token,
    _verify_token,
)
from apps.accounts.utils.nickname_validator import validate_nickname

NICKNAME_PREFIX = "auth:signup:nickname-check:"


def normalize_nickname(nickname: str) -> str:
    return nickname.strip()


def ensure_nickname_not_exists(nickname: str) -> None:
    User = get_user_model()
    if User.objects.filter(nickname=nickname).exists():
        raise ValueError("사용중인 닉네임입니다.")


def issue_nickname_check_token(*, nickname: str) -> CheckResult:
    value = normalize_nickname(nickname)
    validate_nickname(value)
    ensure_nickname_not_exists(value)
    return _issue_token(
        prefix=NICKNAME_PREFIX, value=value, message="사용 가능한 닉네임입니다."
    )


def verify_nickname_check_token(
    *, nickname: str, check_token: str, consume: bool = True
) -> bool:
    value = normalize_nickname(nickname)
    return _verify_token(
        prefix=NICKNAME_PREFIX, value=value, check_token=check_token, consume=consume
    )
