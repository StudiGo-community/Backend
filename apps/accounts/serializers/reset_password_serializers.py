from __future__ import annotations

from typing import Any

from django.contrib.auth import password_validation
from rest_framework import serializers


class ResetPasswordRequestSerializer(serializers.Serializer[Any]):
    email_verify_token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs: Any) -> Any:
        password = attrs.get("new_password")
        password2 = attrs.get("new_password_confirm")
        if password != password2:
            raise serializers.ValidationError(
                {"detail": "비밀번호 확인이 일치하지 않습니다."}
            )

        password_validation.validate_password(password)
        return attrs
