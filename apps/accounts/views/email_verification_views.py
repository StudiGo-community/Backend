from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.email_verification_serializers import (
    EmailConfirmCodeRequestSerializer,
    EmailConfirmCodeResponseSerializer,
    EmailSendCodeResponseSerializer,
    ResetPasswordEmailSendCodeRequestSerializer,
    SignupEmailSendCodeRequestSerializer,
)
from apps.accounts.services.email_verification_services import (
    email_confirm_code,
    reset_password_email_send_code,
    signup_email_send_code,
)
from apps.core.choices.verification_choices import (
    EmailVerificationPurpose,
)


class SignupEmailSendCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_signup_email_send_code",
        summary="회원가입 이메일 인증코드 발송",
        request=SignupEmailSendCodeRequestSerializer,
        responses={200: EmailSendCodeResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = SignupEmailSendCodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = signup_email_send_code(
                email=serializer.validated_data["email"],
                check_token=serializer.validated_data["check_token"],
            )
        except (ValueError, RuntimeError) as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            EmailSendCodeResponseSerializer(
                {
                    "request_id": result.request_id,
                    "expires_in": result.expires_in,
                    "cooldown": result.cooldown,
                }
            ).data,
            status=status.HTTP_200_OK,
        )


class SignupEmailConfirmCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_signup_email_confirm_code",
        summary="회원가입 이메일 인증코드 확인",
        request=EmailConfirmCodeRequestSerializer,
        responses={200: EmailConfirmCodeResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = EmailConfirmCodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = email_confirm_code(
                purpose=EmailVerificationPurpose.SIGNUP,
                email=serializer.validated_data["email"],
                request_id=serializer.validated_data["request_id"],
                verification_code=serializer.validated_data["verification_code"],
            )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            EmailConfirmCodeResponseSerializer(
                {
                    "email_verify_token": result.email_verify_token,
                    "expires_in": result.expires_in,
                }
            ).data,
            status=status.HTTP_200_OK,
        )


class ResetPasswordEmailSendCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_reset_password_email_send_code",
        summary="비밀번호 재설정 이메일 인증코드 발송",
        request=ResetPasswordEmailSendCodeRequestSerializer,
        responses={200: EmailSendCodeResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = ResetPasswordEmailSendCodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = reset_password_email_send_code(
                email=serializer.validated_data["email"]
            )
        except (ValueError, RuntimeError) as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            EmailSendCodeResponseSerializer(
                {
                    "request_id": result.request_id,
                    "expires_in": result.expires_in,
                    "cooldown": result.cooldown,
                }
            ).data,
            status=status.HTTP_200_OK,
        )


class ResetPasswordEmailConfirmCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["유저"],
        operation_id="auth_reset_password_email_confirm_code",
        summary="비밀번호 재설정 이메일 인증코드 확인",
        request=EmailConfirmCodeRequestSerializer,
        responses={200: EmailConfirmCodeResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = EmailConfirmCodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = email_confirm_code(
                purpose=EmailVerificationPurpose.PASSWORD_RESET,
                email=serializer.validated_data["email"],
                request_id=serializer.validated_data["request_id"],
                verification_code=serializer.validated_data["verification_code"],
            )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            EmailConfirmCodeResponseSerializer(
                {
                    "email_verify_token": result.email_verify_token,
                    "expires_in": result.expires_in,
                }
            ).data,
            status=status.HTTP_200_OK,
        )
