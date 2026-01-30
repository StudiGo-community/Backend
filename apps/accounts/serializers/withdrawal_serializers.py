from __future__ import annotations

from typing import Any

from rest_framework import serializers


class WithdrawalTokenMethodResponseSerializer(serializers.Serializer[Any]):
    next_step = serializers.ChoiceField(choices=["password", "social"])
    providers = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )


class WithdrawalSerializer(serializers.Serializer[Any]):
    withdrawal_token = serializers.CharField(
        write_only=True, required=False, allow_blank=False
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "인증이 필요합니다."})

        if not attrs.get("withdrawal_token"):
            raise serializers.ValidationError(
                {"detail": "탈퇴 인증 토큰이 필요합니다."}
            )

        return attrs


class WithdrawalIssueTokenByPasswordSerializer(serializers.Serializer[Any]):
    password = serializers.CharField(write_only=True, allow_blank=False)


class WithdrawalIssueTokenResponseSerializer(serializers.Serializer[Any]):
    withdrawal_token = serializers.CharField()
    expires_in = serializers.IntegerField()
