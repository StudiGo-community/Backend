from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.reset_password_serializers import (
    ResetPasswordRequestSerializer,
)
from apps.accounts.services.reset_password_services import reset_password


class PasswordResetView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["유저"],
        operation_id="auth_reset_password",
        summary="비밀번호 재설정",
        description="이메일 인증을 거친 후 비밀번호를 재설정합니다.",
        request=ResetPasswordRequestSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "message": "string",
                        "example": "비밀번호가 재설정되었습니다.",
                    }
                },
            }
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_password(
            email_verify_token=serializer.validated_data["email_verify_token"],
            new_password=serializer.validated_data["new_password"],
        )

        return Response(
            {"message": "비밀번호가 재설정되었습니다."}, status=status.HTTP_200_OK
        )
