from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.check_email_serializers import (
    CheckEmailRequestSerializer,
    CheckEmailResponseSerializer,
)
from apps.accounts.services.check_email_services import issue_email_check_token


class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_check_email",
        summary="이메일 중복 체크",
        description="이메일이 사용 가능한지 체크합니다.",
        request=CheckEmailRequestSerializer,
        responses={200: CheckEmailResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = CheckEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = issue_email_check_token(email=serializer.validated_data["email"])
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        data = {
            "message": result.message,
            "check_token": result.check_token,
            "expires_in": result.expires_in,
        }
        return Response(
            CheckEmailResponseSerializer(data).data, status=status.HTTP_200_OK
        )
