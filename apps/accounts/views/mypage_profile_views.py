from typing import Any

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.profile_serializers import (
    PasswordChangeSerializer,
    ProfileImageSerializer,
    ProfileUpdateSerializer,
)
from apps.accounts.services.mypage.password_change_service import PasswordService
from apps.accounts.services.mypage.profile_service import MyPageProfileService


# 공통상속 permission
class PermissionClass(APIView):
    permission_classes = (IsAuthenticated,)


"""
api/v1/users/me/profile
프로필 조회  GET
프로필 수정  PATCH
"""


class ProfileView(PermissionClass):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.profile_service = MyPageProfileService()

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 유저 프로필 조회",
        description=(
            "사용자가 마이페이지에서 본인의 기본 프로필 정보를 조회합니다.\n\n"
            "**표시 정보:**\n"
            "- 프로필 이미지\n"
            "- 닉네임\n"
            "- 이메일\n"
            "- 가입일"
        ),
        responses={
            200: OpenApiResponse(description="프로필 조회 성공"),
            401: OpenApiResponse(description="인증 실패"),
        },
        examples=[
            OpenApiExample(
                name="프로필 조회 성공",
                description="인증된 사용자가 본인 프로필을 정상 조회한 경우",
                value={
                    "user": {
                        "id": 1,
                        "email": "andrew@example.com",
                        "nickname": "로베르토",
                        "name": "Roberto",
                        "profile_image_url": "url",
                        "gender": "MALE",
                        "birthday": "1995-03-21",
                        "phone": "01012345678",
                        "role": "USER",
                        "created_at": "2026-01-01T12:34:56+09:00",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="인증 실패",
                description='미인증 요청일 때 (오류 메시지: "Authentication credentials were not provided.")',
                value={"detail": "Authentication credentials were not provided."},
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
    def get(self, request: Request) -> Response:
        user = self.profile_service.get_authenticated_user(request)
        data = self.profile_service.get_profile(user)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 유저 프로필 수정",
        description=(
            "사용자가 본인의 프로필 정보를 수정할 수 있습니다.\n\n"
            "**수정 가능한 항목:**\n"
            "- 닉네임\n"
            "- 프로필 이미지\n"
            "- 전화번호"
        ),
        request=ProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(description="프로필 수정 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 실패"),
        },
        examples=[
            OpenApiExample(
                name="프로필 수정 성공",
                description="프로필 수정 후 응답",
                value={
                    "message": "프로필이 수정됐습니다.",
                    "user": {
                        "id": 1,
                        "email": "andrew@example.com",
                        "nickname": "앤드류",
                        "name": "Andrew Song",
                        "profile_image_url": "https://cdn.example.com/profiles/1.png",
                        "gender": "MALE",
                        "birthday": "1995-03-21",
                        "phone": "01012345678",
                        "role": "USER",
                        "created_at": "2026-01-10T09:15:00+09:00",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="유효성 검사 실패",
                description="입력값 형식 오류",
                value={"nickname": ["닉네임 형식이 올바르지 않습니다."]},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def patch(self, request: Request) -> Response:
        user = self.profile_service.get_authenticated_user(request)
        serializer = ProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = self.profile_service.update_profile(user, serializer.validated_data)

        if not result.success:
            return Response({"error": result.error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "프로필이 수정됐습니다.", "user": result.data},
            status=status.HTTP_200_OK,
        )


"""
api/v1/users/me/profile/password
비밀번호 변경 PUT
"""


class PasswordChangeView(PermissionClass):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.profile_service = MyPageProfileService()

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 유저 비밀번호 변경",
        description="사용자가 비밀번호를 변경합니다.\n\n"
        "**필수 입력:**\n"
        "- current_password: 현재 비밀번호\n"
        "- new_password: 새 비밀번호\n"
        "- new_password_confirm: 새 비밀번호 확인\n"
        "\n**검증 사항:**\n"
        "- 현재 비밀번호 일치 여부\n"
        "- 새 비밀번호 일치 여부\n"
        "- 현재 비밀번호와 새 비밀번호 다름 여부\n",
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description="비밀번호 변경 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 실패"),
        },
        examples=[
            OpenApiExample(
                name="비밀번호 변경 성공",
                value={},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="현재 비밀번호 불일치",
                value={"error": "현재 비밀번호가 일치하지 않습니다."},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def put(self, request: Request) -> Response:
        user = self.profile_service.get_authenticated_user(request)

        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        result = PasswordService.change_password(
            user=user,
            current_password=data["current_password"],
            new_password=data["new_password"],
            new_password_confirm=data["new_password_confirm"],
        )

        if not result.success:
            return Response({"error": result.error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


"""
프로필 이미지 수정 API

api/v1/users/me/profile/image
이미지 URL 업데이트 PATCH

api/v1/users/me/profile/image
이미지 삭제 DELETE
"""


class ProfileImageView(APIView):

    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.profile_service = MyPageProfileService()

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 프로필 이미지 수정",
        description=(
            "프로필 이미지 URL을 업데이트합니다.\n\n"
            "FE에서 S3 업로드 후 반환된 URL을 전달합니다."
        ),
        request=ProfileImageSerializer,
        examples=[
            OpenApiExample(
                name="이미지 수정 선공",
                description="이미지 URL 업데이트 성공",
                value={
                    "message": "프로필이 수정되었습니다.",
                    "user": {
                        "id": 12345,
                        "nickname": "새로운닉네임",
                        "profile_image_url": "https://cdn.studigo.com/profiles/12345_new.png",
                        "updated_at": "2026-01-09T15:30:00Z",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def patch(self, request: Request) -> Response:
        user = self.profile_service.get_authenticated_user(request)

        serializer = ProfileImageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = self.profile_service.update_profile_image(
            user,
            serializer.validated_data["profile_image_url"],
        )

        if not result.success:
            return Response({"error": result.error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "프로필이 수정되었습니다.", "user": result.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 프로필 이미지 삭제",
        description="프로필 이미지를 삭제합니다.",
        responses={
            200: OpenApiResponse(description="프로필 이미지 삭제 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 실패"),
        },
        examples=[
            OpenApiExample(
                name="이미지 삭제 성공",
                value={"message": "프로필 이미지가 삭제되었습니다."},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def delete(self, request: Request) -> Response:
        user = self.profile_service.get_authenticated_user(request)
        result = self.profile_service.delete_profile_image(user)

        if not result.success:
            return Response({"error": result.error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "프로필 이미지가 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
