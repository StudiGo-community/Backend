from __future__ import annotations

from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.chat.models import MessageReport
from apps.chat.models.message import Message
from apps.chat.serializers.message_report import (
    MessageReportCreateResponseSerializer,
    MessageReportCreateSerializer,
)


class MessageReportCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="메세지 신고",
        tags=["채팅"],
        request=MessageReportCreateSerializer,
        responses={201: MessageReportCreateResponseSerializer},
    )
    def post(self, request: Request, message_id: int) -> Response:
        user = cast(User, request.user)

        serializer = MessageReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response(
                {"detail": "메시지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 중복 신고 방지 (DB constraint + 사전 체크)
        if MessageReport.objects.filter(reporter=user, message=message).exists():
            return Response(
                {"detail": "이미 신고한 메시지입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        MessageReport.objects.create(
            reporter=user,
            message=message,
            reason=serializer.validated_data["reason"],
        )

        return Response(
            {"message": "신고가 접수되었습니다."},
            status=status.HTTP_201_CREATED,
        )
