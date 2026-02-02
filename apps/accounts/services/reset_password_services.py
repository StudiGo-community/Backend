from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ValidationError

from apps.accounts.services.check_email_services import normalize_email
from apps.accounts.utils.verify_token import verify_and_consume
from apps.core.enumeration.account_verification_enumeration import (
    EmailVerificationPurpose,
)

User = get_user_model()


def reset_password(*, email_verify_token: str, new_password: str) -> None:
    try:
        claims = verify_and_consume(
            email_verify_token,
            expected_purpose=EmailVerificationPurpose.PASSWORD_RESET,
        )
    except AuthenticationFailed:
        raise ValidationError({"detail": "검증 토큰이 유효하지 않거나 만료되었습니다."})

    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub:
        raise ValidationError({"detail": "검증 토큰이 유효하지 않거나 만료되었습니다."})

    email = normalize_email(sub)

    user = User.objects.filter(email=email).first()
    if not user:
        raise ValidationError({"detail": "등록된 이메일이 아닙니다."})

    if not user.has_usable_password():
        raise ValidationError(
            {
                "detail": "해당 계정은 소셜 로그인으로 가입된 계정입니다. 소셜 로그인을 이용해주세요."
            }
        )

    user.set_password(new_password)
    user.save(update_fields=["password"])
