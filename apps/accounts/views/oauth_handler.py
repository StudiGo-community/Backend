from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response

from apps.accounts.models.users import OAuthAccount
from apps.accounts.services.auth_services import issue_tokens
from apps.accounts.utils.cookies import set_access_cookie, set_refresh_cookie
from apps.accounts.utils.session_cache import (
    SocialSession,
    save_signup_session,
)
from apps.accounts.utils.verify_token import issue_verify_token
from apps.core.security import JWT_ACCESS_TOKEN_LIFETIME


class OAuthNextStatus:
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    SIGNUP_REQUIRED = "SIGNUP_REQUIRED"
    LINK_REQUIRED = "LINK_REQUIRED"


ACCESS_LIFETIME = timedelta(seconds=JWT_ACCESS_TOKEN_LIFETIME)


def handle_social_callback(
    *,
    provider: str,
    provider_user_id: str | None,
    email: str | None,
    name: str | None,
    picture: str | None,
    purpose: str = "login",
) -> Response:
    if not provider_user_id:
        raise AuthenticationFailed({"detail": "소셜 인증 처리에 실패했습니다."})

    # 회원 탈퇴 전 소셜 재인증 - 기존 연동 계정인지 확인 후 토큰 발급
    if purpose == "withdrawal":
        oauth_account = (
            OAuthAccount.objects.select_related("user")
            .filter(provider=provider, provider_user_id=provider_user_id)
            .first()
        )
        if not oauth_account:
            raise AuthenticationFailed({"detail": "소셜 재인증에 실패했습니다."})

        user = oauth_account.user
        if user.pk is None:
            raise AuthenticationFailed({"detail": "소셜 재인증에 실패했습니다."})

        token = issue_verify_token(sub=str(user.pk), purpose="withdrawal")
        ttl = int(getattr(settings, "VERIFY_TOKEN_EXPIRES_SECONDS", 600))
        return Response(
            {
                "status": "WITHDRAWAL_VERIFIED",
                "withdrawal_token": token,
                "expires_in": ttl,
            },
            status=status.HTTP_200_OK,
        )

    # 이메일 필수
    if not email:
        raise ValidationError(
            {"detail": "이메일 제공에 동의해야 소셜 로그인이 가능합니다."}
        )

    User = get_user_model()

    # 이미 연동된 소셜 계정 → 로그인
    oauth_account = (
        OAuthAccount.objects.select_related("user")
        .filter(provider=provider, provider_user_id=provider_user_id)
        .first()
    )
    if oauth_account:
        user = oauth_account.user

        access, refresh, refresh_max_age = issue_tokens(user=user, remember_me=False)
        access_max_age = int(ACCESS_LIFETIME.total_seconds())

        response = Response(
            {"status": OAuthNextStatus.LOGIN_SUCCESS},
            status=status.HTTP_200_OK,
        )
        set_access_cookie(response, access, max_age=access_max_age)
        set_refresh_cookie(response, refresh, max_age=refresh_max_age)
        return response

    # 동일 이메일의 기존 계정 존재 → 연동
    if User.objects.filter(email=email).exists():
        session_id = uuid.uuid4().hex
        save_signup_session(
            session_id,
            SocialSession(
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
                name=name,
                picture=picture,
            ),
        )
        return Response(
            {
                "status": OAuthNextStatus.LINK_REQUIRED,
                "session_id": session_id,
            },
            status=status.HTTP_200_OK,
        )

    # 신규 소셜 가입
    session_id = uuid.uuid4().hex
    save_signup_session(
        session_id,
        SocialSession(
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
            picture=picture,
        ),
    )
    return Response(
        {
            "status": OAuthNextStatus.SIGNUP_REQUIRED,
            "session_id": session_id,
        },
        status=status.HTTP_200_OK,
    )
