from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

"""
UserProfileSerializer
유저 프로필 직렬화

ProfileUpdateSerializer
프로필 수정 입력 직렬화

ProfileImageSerializer
프로필 이미지 업로드 입력 직렬화

PasswordChangeSerializer
비밀번호 변경 입력 직렬화
"""

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer[Any]):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = [
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
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.Serializer[Any]):
    nickname = serializers.CharField(max_length=10, required=False)
    image = serializers.URLField()  # 이미지 이거 맞던가?


class PasswordChangeSerializer(serializers.Serializer[Any]):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)
