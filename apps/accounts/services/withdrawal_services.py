from __future__ import annotations

from typing import Any, cast

from django.db.models import Count, F
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.services.auth_services import logout
from apps.accounts.utils.verify_token import verify_and_consume
from apps.community.models.post_likes import PostLike
from apps.community.models.posts import Post


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

    # post별로 집계해서 like_count 차감
    like_rows = (
        cast(Any, PostLike)
        .objects.filter(user=user)
        .values("post_id")
        .annotate(cnt=Count("id"))
    )
    for row in like_rows:
        cast(Any, Post).objects.filter(pk=row["post_id"]).update(
            like_count=F("like_count") - row["cnt"]
        )

    # 하드 삭제
    user.delete()
