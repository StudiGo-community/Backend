# apps/accounts/views/signup_views.py
from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.signup_serializers import (
    SignupRequestSerializer,
    SignupResponseSerializer,
)
from apps.accounts.services.signup_services import signup_email


class EmailSignupView(APIView):
    authentication_classes: list[Any] = []
    permission_classes: list[Any] = []

    @extend_schema(
        tags=["유저"],
        operation_id="auth_signup",
        summary="이메일 회원가입",
        description="이메일을 사용해 회원가입을 합니다.",
        request=SignupRequestSerializer,
        responses={200: SignupResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = signup_email(data=serializer.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = SignupResponseSerializer(
            {
                "id": result.user.id,
                "email": result.user.email,
                "nickname": result.user.nickname,
                "name": result.user.name,
                "gender": result.user.gender,
                "phone": result.user.phone,
                "birthday": result.user.birthday,
                "agree_marketing": result.user.agree_marketing,
                "created_at": result.user.created_at,
            }
        )
        return Response(response.data, status=status.HTTP_201_CREATED)
