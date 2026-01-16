from typing import Any

from rest_framework import serializers

from apps.accounts.models.users import User

"""
LoginSerializer: 로그인 시 사용. POST
검증: 이메일/비밀번호 일치, 계정 상태.
"""


class LoginSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "gender",
            "phone",
            "birthday",
            "profile_image_url",
            "status",
            "role",
            "created_at",
            "updated_at",
        ]
