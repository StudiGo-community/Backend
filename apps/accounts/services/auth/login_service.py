from apps.accounts.models.users import User
from apps.accounts.services.auth.errors import AuthServiceError
from apps.core.enumeration.account_user_enumeration import UserStatus


class AuthLoginService:
    @staticmethod
    def authenticate_and_validate(*, email: str, password: str) -> User:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthServiceError({"detail": "이메일 또는 비밀번호를 확인해주세요."})

        if not user.check_password(password):
            raise AuthServiceError({"detail": "이메일 또는 비밀번호를 확인해주세요."})

        if not user.is_active:
            raise AuthServiceError(
                {
                    "detail": "비활성화된 계정입니다. 관리자에게 문의하세요.",
                    "error_code": "ACCOUNT_INACTIVE",
                }
            )

        if user.status == UserStatus.BANNED:
            raise AuthServiceError(
                {"detail": "정지된 계정입니다.", "error_code": "ACCOUNT_BANNED"}
            )

        return user
