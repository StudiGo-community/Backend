# JWT 인증 미들웨어
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework_simplejwt.authentication import JWTAuthentication


@database_sync_to_async
def _get_user_from_token(token: str):
    close_old_connections()
    jwt_auth = JWTAuthentication()
    validated = jwt_auth.get_validated_token(token)
    return jwt_auth.get_user(validated)


class JwtAuthMiddleware:
    """
    ws://.../?token=<access_token>
    으로 들어온 토큰을 검증해서 scope["user"]를 채워준다.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope: dict[str, Any], receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = (query.get("token") or [None])[0]

        scope["user"] = AnonymousUser()
        if token:
            try:
                scope["user"] = await _get_user_from_token(token)
            except Exception:
                scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
