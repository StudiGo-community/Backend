from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.accounts.models.users import OAuthAccount
from apps.accounts.utils.session_cache import (
    delete_signup_session,
    load_signup_session,
    mark_used_once,
)


@dataclass(frozen=True)
class SocialSignupCompleteCommand:
    session_id: str
    nickname: str
    phone: str
    gender: str
    agree_terms: bool
    agree_privacy: bool
    agree_marketing: bool


@dataclass(frozen=True)
class SocialLinkConfirmCommand:
    session_id: str
    email: str
    password: str


def complete_social_signup(*, command: SocialSignupCompleteCommand) -> Any:
    """
    - Redis signup session 로드
    - used 1회성 체크
    - User 생성
    - OAuthAccount 생성
    - signup session 삭제
    """
    if not mark_used_once(command.session_id):
        raise ValidationError(
            {"detail": "가입 세션이 만료되었거나 이미 사용되었습니다."}
        )

    session = load_signup_session(command.session_id)
    if not session:
        raise ValidationError(
            {"detail": "가입 세션이 만료되었거나 이미 사용되었습니다."}
        )

    provider = str(session.get("provider") or "")
    provider_user_id = str(session.get("provider_user_id") or "")
    email = session.get("email")

    if not provider or not provider_user_id:
        raise ValidationError({"detail": "가입 세션이 올바르지 않습니다."})

    if not email:
        raise ValidationError(
            {"detail": "이메일 제공에 동의해야 소셜 로그인이 가능합니다."}
        )

    User = get_user_model()

    name = (session.get("name") or command.nickname)[:10]
    picture = session.get("picture")

    try:
        with transaction.atomic():
            # 소셜 계정이 이미 등록되어 있는지 확인
            if (
                OAuthAccount.objects.select_for_update()
                .filter(
                    provider=provider,
                    provider_user_id=provider_user_id,
                )
                .exists()
            ):
                raise ValidationError({"detail": "이미 가입된 소셜 계정입니다."})

            # 이메일 계정이 이미 있는지 확인
            if User.objects.select_for_update().filter(email=email).exists():
                raise ValidationError(
                    {"detail": "해당 이메일로 가입된 계정이 있습니다."}
                )

            # 닉네임 / 휴대폰 번호 중복 체크
            if (
                User.objects.select_for_update()
                .filter(nickname=command.nickname)
                .exists()
            ):
                raise ValidationError({"detail": "이미 사용 중인 닉네임입니다."})

            if User.objects.select_for_update().filter(phone=command.phone).exists():
                raise ValidationError({"detail": "이미 등록된 휴대폰 번호입니다."})

            user = User.objects.create_user(
                email=email,
                password=None,
                nickname=command.nickname,
                name=name,
                gender=command.gender,
                phone=command.phone,
                profile_image_url=picture,
                is_active=True,
                agree_marketing=command.agree_marketing,
            )

            OAuthAccount.objects.create(
                user=user,
                provider=provider,
                provider_user_id=provider_user_id,
            )

    except ValidationError:
        raise
    except IntegrityError:
        raise ValidationError(
            {"detail": "요청을 처리할 수 없습니다. 다시 시도해주세요."}
        )

    delete_signup_session(command.session_id)
    return user


def confirm_social_link(*, command: SocialLinkConfirmCommand) -> Any:
    """
    - Redis signup session 로드
    - used 1회성 체크
    - 이메일 가입 계정의 비밀번호 확인
    - OAuthAccount 생성(연동)
    - signup session 삭제
    """
    if not mark_used_once(command.session_id):
        raise ValidationError(
            {"detail": "연동 세션이 만료되었거나 이미 사용되었습니다."}
        )

    session = load_signup_session(command.session_id)
    if not session:
        raise ValidationError(
            {"detail": "연동 세션이 만료되었거나 이미 사용되었습니다."}
        )

    provider = str(session.get("provider") or "")
    provider_user_id = str(session.get("provider_user_id") or "")
    session_email = session.get("email")

    if not provider or not provider_user_id:
        raise ValidationError({"detail": "연동 세션이 올바르지 않습니다."})

    if not session_email:
        raise ValidationError(
            {"detail": "이메일 제공에 동의해야 소셜 로그인이 가능합니다."}
        )

    # 세션 이메일과 요청 이메일 일치 강제
    if session_email.lower().strip() != command.email.lower().strip():
        raise ValidationError({"detail": "요청값이 올바르지 않습니다."})

    User = get_user_model()
    try:
        user = User.objects.get(email=command.email)
    except User.DoesNotExist:
        raise ValidationError(
            {"detail": "해당 이메일로 가입된 계정을 찾을 수 없습니다."}
        )

    if not user.has_usable_password():
        raise AuthenticationFailed({"detail": "비밀번호가 없는 계정입니다."})

    if not user.check_password(command.password):
        raise AuthenticationFailed({"detail": "비밀번호가 올바르지 않습니다."})

    try:
        with transaction.atomic():
            if (
                OAuthAccount.objects.select_for_update()
                .filter(
                    provider=provider,
                    provider_user_id=provider_user_id,
                )
                .exists()
            ):
                raise ValidationError(
                    {"detail": "이미 다른 계정에 연동된 소셜 계정입니다."}
                )

            OAuthAccount.objects.create(
                user=user,
                provider=provider,
                provider_user_id=provider_user_id,
            )

    except ValidationError:
        raise
    except IntegrityError:
        raise ValidationError(
            {"detail": "요청을 처리할 수 없습니다. 다시 시도해주세요."}
        )

    delete_signup_session(command.session_id)
    return user
