from dataclasses import dataclass

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models.users import User


@dataclass
class PasswordChangeResult:
    success: bool
    error: str | None = None


class PasswordService:

    @classmethod
    def change_password(
        cls,
        user: User,
        current_password: str,
        new_password: str,
        new_password_confirm: str,
    ) -> PasswordChangeResult:

        # 현재 비밀번호 확인
        if not user.check_password(current_password):
            return PasswordChangeResult(
                success=False,
                error="현재 비밀번호가 올바르지 않습니다.",
            )

        # 새 비밀번호 일치 확인
        if new_password != new_password_confirm:
            return PasswordChangeResult(
                success=False,
                error="새 비밀번호가 일치하지 않습니다.",
            )

        # 현재 비밀번호와 동일 여부 확인
        if current_password == new_password:
            return PasswordChangeResult(
                success=False,
                error="현재 비밀번호와 다른 비밀번호를 입력해주세요.",
            )

        # Django 기본 비밀번호 유효성 검사
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            # 메시지가 여러 개인 경우를 합쳐서 전달 + 비어있는 경우 fallback
            msg = (
                " / ".join(e.messages)
                if e.messages
                else "비밀번호가 유효하지 않습니다."
            )
            return PasswordChangeResult(success=False, error=msg)

        # 비밀번호 변경 (DB 반영)
        with transaction.atomic():
            user.set_password(new_password)

            # updated_at이 있는지 확실하지 않으면 안전하게 처리
            update_fields = ["password"]
            if hasattr(user, "updated_at"):
                update_fields.append("updated_at")

            user.save(update_fields=update_fields)

        return PasswordChangeResult(success=True)
