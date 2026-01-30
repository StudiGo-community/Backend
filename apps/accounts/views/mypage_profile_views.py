from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.profile_serializers import ProfileUpdateSerializer
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
        description="사용자가 마이페이지에 접속하여 본인의 기본 프로필 정보를 조회합니다."
        "마이페이지 접근 경로:"
        "- 웹 페이지 우측 상단의 프로필 아이콘 클릭"
        "- 모달 메뉴에서 [마이페이지] 클릭"
        "프로필 조회 시 표시되는 정보:"
        "- 프로필 이미지"
        "- 닉네임"
        "- 이메일"
        "- 가입일"
        "- 오늘 출석 여부(출석 시: 오늘 출석 완료!)"
        "**Query Parameters:**\n"
        "- blank",
    )
    def get(self, request: Request) -> Response:
        user = self.profile_service.get_authenticated_user(request)
        data = self.profile_service.get_profile(user)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 유저 프로필 수정",
        description="사용자가 본인의 프로필 정보를 수정할 수 있습니다.\n\n"
        "*수정 가능한 항목:*"
        "- 닉네임"
        "- 프로필 이미지"
        "*닉네임 수정:*"
        "- 닉네임 규칙"
        "- 중복 확인 필수"
        "- 현재 닉네임과 동일한 경우 중복 확인 없이 통과"
        "- 디폴트로 현재 닉네임 입력되어 있음"
        ""
        "*프로필 이미지 수정:*"
        "- 이미지 없음(기본?)"
        "- 기본 제공 이미지 중 선택"
        "- 직접 이미지 업로드",
        request=ProfileUpdateSerializer,
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
api/v1/users/me/profile/image
프로필 이미지 업로드 POST
"""


class ProfileImageView(PermissionClass):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=["마이페이지"],
        summary="마이페이지 유저 비밀번호 변경 API",
        description="" "" "" "",
    )
    def post(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)


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
    )
    def put(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)
