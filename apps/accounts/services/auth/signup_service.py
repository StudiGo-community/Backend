from datetime import date
from typing import Any

from django.db import IntegrityError, transaction

from apps.accounts.models.users import User
from apps.accounts.services.auth.errors import AuthServiceError
from apps.accounts.services.auth.unique_check import AuthUniquenessService


class AuthSignupService:
    @staticmethod
    def validate_signup_payload(
        *,
        email: str,
        password: str,
        password_confirm: str,
        nickname: str,
        phone: str,
        terms_agreed: bool,
        privacy_agreed: bool,
    ) -> None:

        # 비밀번호 확인(기존 serializer → 서비스 이동)
        if password != password_confirm:
            raise AuthServiceError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )

        # 약관 정책
        if not terms_agreed:
            raise AuthServiceError({"terms_agreed": "이용약관에 동의해주세요."})
        if not privacy_agreed:
            raise AuthServiceError(
                {"privacy_agreed": "개인정보처리방침에 동의해주세요."}
            )

        # 중복 정책
        AuthUniquenessService.assert_email_available(email)
        AuthUniquenessService.assert_nickname_available(nickname)
        AuthUniquenessService.assert_phone_available(phone)

    # 토큰 저장 검증 서비스 진행해야 함!
    @staticmethod
    def signup(
        *,
        email: str,
        password: str,
        nickname: str,
        name: str,
        gender: Any,
        phone: str,
        birthday: date,
        email_verification_token: str,
        phone_verification_token: str,
        terms_agreed: bool,
        privacy_agreed: bool,
        marketing_agreed: bool = False,
    ) -> User:
        AuthSignupService.validate_signup_payload(
            email=email,
            password=password,
            password_confirm=password,
            nickname=nickname,
            phone=phone,
            terms_agreed=terms_agreed,
            privacy_agreed=privacy_agreed,
        )

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    nickname=nickname,
                    name=name,
                    gender=gender,
                    phone=phone,
                    birthday=birthday,
                    is_active=True,
                )
                return user
        except IntegrityError:
            # DB Unique constraint 충돌 시
            raise AuthServiceError(
                {
                    "detail": "회원가입 처리 중 중복 데이터가 발생했습니다. 다시 시도해주세요."
                }
            )
