from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from apps.accounts.services.check_email_services import (
    normalize_email,
    verify_email_check_token,
)
from apps.accounts.services.check_nickname_services import (
    normalize_nickname,
    verify_nickname_check_token,
)
from apps.accounts.utils.nickname_validator import validate_nickname
from apps.accounts.utils.verify_token import verify_and_consume
from apps.core.enumeration.account_verification_enumeration import (
    EmailVerificationPurpose,
)

User = get_user_model()


@dataclass(frozen=True)
class SignupResult:
    user: Any


@transaction.atomic
def signup_email(*, data: dict[str, Any]) -> SignupResult:
    email = normalize_email(data["email"])
    nickname = normalize_nickname(data["nickname"])

    nickname_check_token = data["nickname_check_token"]
    email_verify_token = data["email_verify_token"]

    # 닉네임 중복 확인 토큰 소진
    validate_nickname(nickname)
    if not verify_nickname_check_token(
        nickname=nickname, check_token=nickname_check_token, consume=True
    ):
        raise ValueError("닉네임 중복 확인이 필요합니다. 다시 확인해주세요.")

    # 이메일 인증 토큰 검증 (purpose=SIGNUP + sub=email 일치)
    verify_and_consume(
        data["email_verify_token"],
        expected_purpose=EmailVerificationPurpose.SIGNUP,
        expected_sub=email,
    )

    # 유저 생성
    try:
        user = User(
            email=email,
            nickname=nickname,
            name=data["name"],
            gender=data["gender"],
            birthday=data.get("birthday"),
            agree_marketing=data["agree_marketing"],
        )
        user.set_password(data["password"])
        user.save()
    except IntegrityError:
        raise ValueError("이미 가입된 정보입니다.")

    return SignupResult(user=user)
