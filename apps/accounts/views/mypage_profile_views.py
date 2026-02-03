from typing import Any

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.profile_serializers import ProfileUpdateSerializer, PasswordChangeSerializer, ProfileImageSerializer
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
        description="사용자가 마이페이지에 접속하여 본인의 기본 프로필 정보를 조회합니다.\n\n"
        "**마이페이지 접근 경로:**\n\n"
        "- 웹 페이지 우측 상단의 프로필 아이콘 클릭\n"
        "- 모달 메뉴에서 [마이페이지] 클릭\n"
        "\n\n"
        "**프로필 조회 시 표시되는 정보:**\n"
        "- 프로필 이미지\n"
        "- 닉네임\n"
        "- 이메일\n"
        "- 가입일\n"
        "- 오늘 출석 여부(출석 시: 오늘 출석 완료!)\n"
        "\n\n"
        "**Query Parameters:**\n"
        "- blank",
        examples=[
            OpenApiExample(
                name="올바른 예시(200)",
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
                status_codes=[200],
            ),
            OpenApiExample(
                name="실패 응답 예시 - 인증 실패",
                description='미인증 요청일 때 (오류 메세지: "Authentication credentials were not provided.")',
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
        description="사용자가 본인의 프로필 정보를 수정할 수 있습니다.\n\n"
        "**수정 가능한 항목:**\n"
        "- 닉네임\n"
        "- 프로필 이미지"
        "\n\n"
        "**닉네임 수정:**\n"
        "- 닉네임 규칙\n"
        "- 중복 확인 필수\n"
        "- 현재 닉네임과 동일한 경우 중복 확인 없이 통과\n"
        "- 디폴트로 현재 닉네임 입력되어 있음\n"
        "\n\n"
        "**프로필 이미지 수정:**\n"
        "- FE에서 S3 업로드 후 URL 전달\n"
        "- 빈 문자열 또는 null 전달 시 이미지 삭제"
        "- 이미지 없음(기본?)\n"
        "- 기본 제공 이미지 중 선택\n"
        "- 직접 이미지 업로드",
        request=ProfileUpdateSerializer,
        examples=[
            OpenApiExample(
                name="성공 응답 예시(200)",
                description="인증된 사용자가 본인 프로필을 정상 조회한 경우",
                value={
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
                    }
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="실패 응답 예시 - 인증 실패(401)",
                description='미인증 요청일 때 (오류 메세지: "Authentication credentials were not provided.")',
                value={"detail": "Authentication credentials were not provided."},
                response_only=True,
                status_codes=["401"],
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

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 프로필 이미지 삭제",
        description="프로필 이미지를 삭제합니다.",
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


"""
api/v1/users/me/profile/password
비밀번호 변경 PUT
"""


class PasswordChangeView(PermissionClass):
    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 유저 비밀번호 변경",
        description="사용자가 비밀번호를 변경합니다.\n\n"
        "**필수 입력:**\n"
        "- current_password: 현재 비밀번호"
        "- new_password: 새 비밀번호"
        "- new_password_confirm: 새 비밀번호 확인"
        "\n**검증 사항:**"
        "- 현재 비밀번호 일치 여부"
        "- 새 비밀번호 일치 여부"
        "- 현재 비밀번호와 새 비밀번호 다름 여부",
        examples=[],
    )
    def put(self, request: Request) -> Response:
        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        result = PasswordService.change_password(
            user = request.user,
            current_password = data["current_password"],
            new_password = data["new_password"],
            new_password_confirm = data["new_password_confirm"],
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
                name="성공 응답 예시 (200)",
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