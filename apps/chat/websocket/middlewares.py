from __future__ import annotations

from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, cast
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from apps.accounts.models import User

# =========================
# typing helpers
# =========================
P = ParamSpec("P")
R = TypeVar("R")

ASGIReceive = Callable[[], Awaitable[dict[str, Any]]]
ASGISend = Callable[[dict[str, Any]], Awaitable[None]]
ASGIApp = Callable[[dict[str, Any], ASGIReceive, ASGISend], Awaitable[None]]

_typed_db_sync_to_async = cast(
    Callable[[Callable[P, R]], Callable[P, Awaitable[R]]],
    database_sync_to_async,
)


@_typed_db_sync_to_async
def _get_user_from_token(token: str) -> User | AnonymousUser:
    jwt_auth = JWTAuthentication()
    try:
        validated = jwt_auth.get_validated_token(token)  # type: ignore[arg-type]
        user = jwt_auth.get_user(validated)
        return cast(User, user)
    except (InvalidToken, TokenError, Exception):
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):  # type: ignore[misc]
    """
    ws://.../?token=xxxx 형태로 token을 받아 scope['user'] 세팅
    """

    async def __call__(
        self, scope: dict[str, Any], receive: ASGIReceive, send: ASGISend
    ) -> None:
        close_old_connections()

        query_string = scope.get("query_string", b"").decode("utf-8")
        qs = parse_qs(query_string)
        token = qs.get("token", [None])[0]

        if isinstance(token, str) and token:
            scope["user"] = await _get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner: ASGIApp) -> ASGIApp:
    return cast(ASGIApp, JwtAuthMiddleware(inner))
