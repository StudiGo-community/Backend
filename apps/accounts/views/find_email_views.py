from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.find_email_serializers import (
    FindEmailRequestSerializer,
    FindEmailResponseSerializer,
)
from apps.accounts.services.find_email_services import find_masked_email


class FindEmailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_find_email",
        summary="이메일 찾기",
        request=FindEmailRequestSerializer,
        responses={200: FindEmailResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = FindEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masked_email = find_masked_email(**serializer.validated_data)

        return Response(
            FindEmailResponseSerializer(
                {
                    "email": masked_email,
                }
            ).data,
            status=status.HTTP_200_OK,
        )
