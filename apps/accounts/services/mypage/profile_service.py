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

        return ServiceResult(success=True, data=self._serialize_user(user))

    def _serialize_user(self, user: User) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for field in self.USER_FIELDS:
            value = getattr(user, field, None)

            if isinstance(value, (datetime, date)):
                data[field] = value.isoformat()
            else:
                data[field] = value
        return data
