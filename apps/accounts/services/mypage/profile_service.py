from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, cast

from django.db import IntegrityError
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from apps.accounts.models import User
from apps.accounts.serializers.profile_serializers import UserProfileSerializer


@dataclass
class ServiceResult:
    success: bool
    data: Any = None
    error: str | None = None


class MyPageProfileService:

    USER_FIELDS: list[str] = [
        "id",
        "email",
        "nickname",
        "name",
        "profile_image_url",
        "gender",
        "birthday",
        "phone",
        "role",
        "created_at",
    ]

    @staticmethod
    def get_authenticated_user(request: Request) -> User:
        user = request.user
        if not getattr(user, "is_authenticated", False):
            raise NotAuthenticated()
        return cast(User, user)

    def get_profile(self, user: User) -> dict[str, Any]:
        user_data = self._serialize_user(user)
        return {
            "user": user_data,
            # attendance 추가할 것
        }

    def update_profile(self, user: User, data: dict[str, Any]) -> ServiceResult:
        updatable_fields = {"nickname", "phone"}
        update_data: dict[str, Any] = {}
        for k, v in data.items():
            if k in updatable_fields:
                update_data[k] = v

        if not update_data:
            return ServiceResult(success=False, error="수정할 필드가 없습니다.")

        if "nickname" in update_data:
            if not self._is_nickname_available(user, update_data["nickname"]):
                return ServiceResult(
                    success=False, error="이미 사용 중인 닉네임입니다."
                )

        try:
            for field, value in update_data.items():
                setattr(user, field, value)

            update_fields = list(update_data.keys())
            if hasattr(user, "updated_at"):
                update_fields.append("updated_at")

            user.save(update_fields=update_fields)

        except IntegrityError:
            return ServiceResult(success=False, error="프로필 수정에 실패했습니다.")

        return ServiceResult(success=True, data=self._serialize_user(user))

    def update_profile_image(self, user: User, profile_image_url: str) -> ServiceResult:
        """
        프로필 이미지 URL 업데이트

        Args:
            user: 유저 객체
            profile_image_url: 새 이미지 URL

        Returns:
            ServiceResult (id, nickname, profile_image_url, updated_at)
        """
        user.profile_image_url = profile_image_url

        update_fields = ["profile_image_url"]
        if hasattr(user, "updated_at"):
            update_fields.append("updated_at")

        user.save(update_fields=update_fields)

        return ServiceResult(
            success=True,
            data={
                "id": user.id,
                "nickname": user.nickname,
                "profile_image_url": user.profile_image_url,
                "updated_at": (
                    user.updated_at.isoformat() if hasattr(user, "updated_at") else None
                ),
            },
        )

    def delete_profile_image(self, user: User) -> ServiceResult:
        """
        프로필 이미지 삭제 (URL을 None으로)

        Args:
            user: 유저 객체

        Returns:
            ServiceResult
        """
        if not user.profile_image_url:
            return ServiceResult(
                success=False, error="삭제할 프로필 이미지가 없습니다."
            )

        user.profile_image_url = None

        update_fields = ["profile_image_url"]
        if hasattr(user, "updated_at"):
            update_fields.append("updated_at")

        user.save(update_fields=update_fields)

        return ServiceResult(success=True)

    def _is_nickname_available(self, user: User, nickname: str) -> bool:
        """닉네임 사용 가능 여부 확인 (자기 자신 제외, 대소문자 무시)"""
        from apps.accounts.models.users import User as UserModel

        return not (
            UserModel.objects.exclude(pk=user.pk)
            .filter(nickname__iexact=nickname)
            .exists()
        )

    def _serialize_user(self, user: User) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for field in self.USER_FIELDS:
            value = getattr(user, field, None)

            if isinstance(value, (datetime, date)):
                data[field] = value.isoformat()
            else:
                data[field] = value
        return data
