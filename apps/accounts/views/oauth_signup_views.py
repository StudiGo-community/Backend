from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers.oauth_serializers import (
    SocialAuthSResponseSerializer,
    SocialLinkConfirmRequestSerializer,
    SocialSignupCompleteRequestSerializer,
)
from apps.accounts.services.oauth_signup_services import (
    SocialLinkConfirmCommand,
    SocialSignupCompleteCommand,
    complete_social_signup,
    confirm_social_link,
)
from apps.accounts.utils.cookies import set_access_cookie, set_refresh_cookie


def issue_tokens(user: Any) -> dict[str, Any]:
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    return {
        "access": str(access),
        "refresh": str(refresh),
        "access_expires_in": int(access.lifetime.total_seconds()),
        "refresh_expires_in": int(refresh.lifetime.total_seconds()),
    }


class SocialSignupCompleteView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["유저"],
        operation_id="oauth_signup_complete",
        summary="소셜 회원가입 추가정보 입력",
        request=SocialSignupCompleteRequestSerializer,
        responses={200: SocialAuthSResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = SocialSignupCompleteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        command = SocialSignupCompleteCommand(
            session_id=data["session_id"],
            nickname=data["nickname"],
            phone=data["phone"],
            gender=data["gender"],
            agree_terms=data["agree_terms"],
            agree_privacy=data["agree_privacy"],
            agree_marketing=data["agree_marketing"],
        )

        user = complete_social_signup(command=command)

        tokens = issue_tokens(user)
        payload = {
            "token": {
                "access_token": tokens["access"],
                "token_type": "Bearer",
                "expires_in": tokens["access_expires_in"],
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "phone": user.phone,
                "gender": user.gender,
            },
        }

        response = Response(
            SocialAuthSResponseSerializer(payload).data,
            status=status.HTTP_200_OK,
        )
        set_access_cookie(
            response, tokens["access"], max_age=tokens["access_expires_in"]
        )
        set_refresh_cookie(
            response, tokens["refresh"], max_age=tokens["refresh_expires_in"]
        )
        return response


class SocialLinkConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["유저"],
        operation_id="oauth_signup_link",
        summary="소셜 회원가입 계정 연동",
        request=SocialLinkConfirmRequestSerializer,
        responses={200: SocialAuthSResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = SocialLinkConfirmRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        command = SocialLinkConfirmCommand(
            session_id=data["session_id"],
            email=data["email"],
            password=data["password"],
        )

        user = confirm_social_link(command=command)

        tokens = issue_tokens(user)
        payload = {
            "token": {
                "access_token": tokens["access"],
                "token_type": "Bearer",
                "expires_in": tokens["access_expires_in"],
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
            },
        }

        response = Response(
            SocialAuthSResponseSerializer(payload).data,
            status=status.HTTP_200_OK,
        )

        set_access_cookie(
            response, tokens["access"], max_age=tokens["access_expires_in"]
        )
        set_refresh_cookie(
            response, tokens["refresh"], max_age=tokens["refresh_expires_in"]
        )
        return response
