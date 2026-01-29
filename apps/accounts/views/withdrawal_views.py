from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.contrib.auth.hashers import check_password
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.withdrawal_serializers import (
    WithdrawalIssueTokenByPasswordSerializer,
    WithdrawalIssueTokenResponseSerializer,
    WithdrawalSerializer,
)
from apps.accounts.services.withdrawal_services import withdraw_user
from apps.accounts.utils.verify_token import issue_verify_token

if TYPE_CHECKING:
    from apps.accounts.models import User


class WithdrawalIssueTokenByPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["유저"],
        summary="회원탈퇴 인증 토큰 발급(비밀번호)",
        request=WithdrawalIssueTokenByPasswordSerializer,
        responses={200: WithdrawalIssueTokenResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = WithdrawalIssueTokenByPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast("User", request.user)

        password = serializer.validated_data["password"]
        if not user.password:
            raise ValidationError({"detail": "비밀번호가 없는 계정입니다."})

        if not check_password(password, user.password):
            raise AuthenticationFailed({"detail": "비밀번호가 올바르지 않습니다."})

        token = issue_verify_token(
            sub=str(user.pk),
            purpose="withdrawal",
        )
        ttl = int(getattr(settings, "VERIFY_TOKEN_EXPIRES_SECONDS", 600))
        return Response(
            {
                "withdrawal_token": token,
                "expires_in": ttl,
            },
            status=status.HTTP_200_OK,
        )


class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_withdrawal",
        summary="회원 탈퇴",
        description="로그인한 유저가 회원 탈퇴를 진행합니다.",
        request=WithdrawalSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "회원탈퇴가 완료되었습니다.",
                    }
                },
            }
        },
    )
    def post(self, request: Request) -> Response:
        serializer = WithdrawalSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = cast("User", request.user)
        response = Response(
            {"detail": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK
        )

        withdraw_user(
            user=user,
            withdrawal_token=serializer.validated_data["withdrawal_token"],
            request=request,
            response=response,
        )

        return response
