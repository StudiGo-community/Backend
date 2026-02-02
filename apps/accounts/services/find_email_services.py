from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.exceptions import NotFound

from apps.accounts.utils.normalize_phone import normalize_phone

User = get_user_model()


def _mask_email(email: str) -> str:
    """
    이메일 name 부분에서 앞 3글자만 보여주고 나머지 마스킹
    """
    if not email or "@" not in email:
        return ""

    name, domain = email.split("@", 1)

    # 마스킹
    name_visible = name[:3] if len(name) >= 3 else name[:1]
    name_masked = name_visible + "***"

    return f"{name_masked}@{domain}"


def find_masked_email(*, name: str, phone: str) -> str:
    normalized_phone = normalize_phone(phone)

    user = (
        User.objects.filter(
            Q(name=name),
            Q(phone=normalized_phone),
            Q(is_active=True),
        )
        .only("email")
        .first()
    )

    if not user or not getattr(user, "email", None):
        raise NotFound("입력하신 정보와 일치하는 회원 정보가 없습니다.")

    return _mask_email(user.email)
