from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.services.auth_services import logout
from apps.accounts.utils.verify_token import verify_and_consume


def withdraw_user(
    *,
    user: User,
    withdrawal_token: str,
    request: Request,
    response: Response,
) -> None:
    verify_and_consume(
        token=withdrawal_token,
        expected_purpose="withdrawal",
        expected_sub=str(user.pk),
    )

    # 로그아웃 처리 (토큰/쿠키 정리)
    logout(request=request, response=response)

    # 하드 삭제
    user.delete()
