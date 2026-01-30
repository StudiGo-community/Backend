# apps/chat/views/admin_message_view.py
from __future__ import annotations

from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.chat.services.admin_message_delete_service import admin_delete_message


def _is_admin(user: User) -> bool:
    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or getattr(user, "role", "") == "ADMIN"
    )


class AdminMessageDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="메세지 삭제(관리자)", tags=["채팅"])
    def delete(self, request: Request, message_id: int) -> Response:
        admin = cast(User, request.user)

        if not _is_admin(admin):
            return Response(
                {"detail": "관리자 권한이 필요합니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        admin_delete_message(admin=admin, message_id=message_id)

        return Response(
            {"message": "메시지가 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
