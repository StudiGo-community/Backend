from __future__ import annotations

from typing import cast

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.chat.models.message import Message
from apps.chat.serializers.message_report_serializer import (
    MessageReportCreateResponseSerializer,
    MessageReportCreateSerializer,
)
from apps.chat.services.message_report_service import report_message


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
        msg = get_object_or_404(Message, pk=message_id)

        serializer = MessageReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_message(user=user, message=msg, reason=serializer.validated_data["reason"])

        return Response(
            {"message": "신고가 접수되었습니다."},
            status=status.HTTP_201_CREATED,
        )
