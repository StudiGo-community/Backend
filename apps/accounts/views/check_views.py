from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.check_serializers import (
    CheckEmailRequestSerializer,
    CheckNicknameRequestSerializer,
    CheckResponseSerializer,
)
from apps.accounts.services.check_email_services import issue_email_check_token
from apps.accounts.services.check_nickname_services import issue_nickname_check_token


class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_check_email",
        summary="이메일 중복 체크",
        description="이메일이 사용 가능한지 체크합니다.",
        request=CheckEmailRequestSerializer,
        responses={200: CheckResponseSerializer},
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
        return Response(CheckResponseSerializer(data).data, status=status.HTTP_200_OK)


class CheckNicknameView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_check_nickname",
        summary="닉네임 중복 체크",
        description="닉네임이 사용 가능한지 체크합니다.",
        request=CheckNicknameRequestSerializer,
        responses={200: CheckResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = CheckNicknameRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = issue_nickname_check_token(
                nickname=serializer.validated_data["nickname"]
            )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        data = {
            "message": result.message,
            "check_token": result.check_token,
            "expires_in": result.expires_in,
        }
        return Response(CheckResponseSerializer(data).data, status=status.HTTP_200_OK)
