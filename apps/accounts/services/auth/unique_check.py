from apps.accounts.models.users import User
from apps.accounts.services.auth.errors import AuthServiceError


class AuthUniquenessService:
    @staticmethod
    def assert_email_available(email: str) -> None:
        if User.objects.filter(email=email).exists():
            raise AuthServiceError({"email": "이미 가입된 이메일입니다."})

    @staticmethod
    def assert_nickname_available(nickname: str) -> None:
        if User.objects.filter(nickname=nickname).exists():
            raise AuthServiceError({"nickname": "이미 사용 중인 닉네임입니다."})

    @staticmethod
    def assert_phone_available(phone: str) -> None:
        if User.objects.filter(phone=phone).exists():
            raise AuthServiceError({"phone": "이미 가입된 휴대폰 번호입니다."})
