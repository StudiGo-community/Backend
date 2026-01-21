from apps.accounts.serializers.auth.auth_common import Any, BaseMixin, User, serializers

"""
[중복확인]
EmailCheckSerializer
이메일 중복 확인
    POST /api/v1/auth/check-email

EmailCheckResponseSerializer
이메일 중복 확인 응답

NicknameCheckSerializer
닉네임 중복 확인
    POST /api/v1/auth/check-nickname

NicknameCheckResponseSerializer
닉네임 중복 확인 응답
"""


class EmailCheckSerializer(serializers.Serializer[Any], BaseMixin):
    email = BaseMixin.get_email_field()

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value


class EmailCheckResponseSerializer(serializers.Serializer[Any]):
    available = serializers.BooleanField()
    message = serializers.CharField()


class NicknameCheckSerializer(serializers.Serializer[Any], BaseMixin):
    nickname = BaseMixin.get_nickname_field()

    def validate_nickname(self, value: str) -> str:
        # 형식 검증
        value = self.validate_nickname_format(value)
        # 중복 검증
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value


class NicknameCheckResponseSerializer(serializers.Serializer[Any]):

    available = serializers.BooleanField()
    message = serializers.CharField()
