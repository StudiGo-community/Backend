from __future__ import annotations

import secrets
import string
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail

from apps.accounts.services.check_email_services import (
    normalize_email,
    verify_email_check_token,
)
from apps.accounts.utils.verify_token import issue_verify_token
from apps.core.enumeration.account_verification_enumeration import (
    EmailVerificationPurpose,
)

User = get_user_model()


CODE_TTL = int(getattr(settings, "EMAIL_VERIFICATION_CODE_TTL", 60 * 3))
COOLDOWN = int(getattr(settings, "EMAIL_VERIFICATION_COOLDOWN", 30))
MAX_ATTEMPTS = int(getattr(settings, "EMAIL_VERIFICATION_MAX_ATTEMPTS", 5))
LIMIT_PER_HOUR = int(getattr(settings, "EMAIL_VERIFICATION_LIMIT_PER_HOUR", 3))

DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", None)


def _pending_key(purpose: str, email: str, request_id: str) -> str:
    return f"verify:email:pending:{purpose}:{email}:{request_id}"


def _cooldown_key(purpose: str, email: str) -> str:
    return f"verify:email:cooldown:{purpose}:{email}"


def _failcnt_key(purpose: str, email: str, request_id: str) -> str:
    return f"verify:email:failcnt:{purpose}:{email}:{request_id}"


def _lock_key(purpose: str, email: str, request_id: str) -> str:
    return f"verify:email:lock:{purpose}:{email}:{request_id}"


def _hourly_send_cnt_key(purpose: str, email: str) -> str:
    return f"verify:email:sendcnt:reset:{purpose}:{email}"


def _generate_base62_8() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


def _safe_incr(key: str, ttl: int) -> int:
    val = cache.get(key)
    if val is None:
        cache.set(key, 1, timeout=ttl)
        return 1
    try:
        new_val = int(val) + 1
    except (TypeError, ValueError):
        new_val = 1
    cache.set(key, new_val, timeout=ttl)  # 매번 TTL 갱신
    return new_val


@dataclass(frozen=True)
class SendCodeResult:
    request_id: str
    expires_in: int
    cooldown: int


@dataclass(frozen=True)
class ConfirmCodeResult:
    email_verify_token: str
    expires_in: int


def _send_email(*, to: str, code: str, ttl_seconds: int, subject: str) -> None:
    message = (
        f"인증코드: {code}\n"
        f"유효시간: {ttl_seconds}초\n"
        f"본인이 요청하지 않았다면 이 메일을 무시해주세요."
    )
    send_mail(subject, message, DEFAULT_FROM_EMAIL, [to], fail_silently=False)


PrecheckFn = Callable[[str], None]


def _send_code_common(
    *,
    purpose: EmailVerificationPurpose,
    email: str,
    subject: str,
    precheck: PrecheckFn | None = None,
) -> SendCodeResult:
    to = normalize_email(email)
    purpose_value = purpose.value

    # 목적별 사전 검증
    if precheck:
        precheck(to)

    # 1시간 내 발송 제한
    cnt_key = _hourly_send_cnt_key(purpose_value, to)
    current = _safe_incr(cnt_key, 3600)
    if current > LIMIT_PER_HOUR:
        raise ValueError("발송 횟수를 초과했습니다. 1시간 후 다시 시도해주세요.")

    # cooldown
    cd_key = _cooldown_key(purpose_value, to)
    if cache.get(cd_key):
        raise ValueError("재전송 대기 시간이 지나지 않았습니다.")
    cache.set(cd_key, "1", timeout=COOLDOWN)

    code = _generate_base62_8()
    request_id = uuid.uuid4().hex
    pk = _pending_key(purpose_value, to, request_id)
    cache.set(pk, code, timeout=CODE_TTL)

    try:
        _send_email(to=to, code=code, ttl_seconds=CODE_TTL, subject=subject)
    except Exception as e:
        cache.delete(pk)
        cache.delete(cd_key)
        raise RuntimeError(f"이메일 인증코드 발송 실패: {e}")

    return SendCodeResult(request_id=request_id, expires_in=CODE_TTL, cooldown=COOLDOWN)


def signup_email_send_code(*, email: str, check_token: str) -> SendCodeResult:
    def precheck(to: str) -> None:
        # check_email 단계 통과(consume=False)
        if not verify_email_check_token(
            email=to, check_token=check_token, consume=False
        ):
            raise ValueError("이메일 중복 확인이 필요합니다. 다시 확인해주세요.")

    return _send_code_common(
        purpose=EmailVerificationPurpose.SIGNUP,
        email=email,
        subject="[Studigo] 이메일 인증코드",
        precheck=precheck,
    )


def reset_password_email_send_code(*, email: str) -> SendCodeResult:
    def precheck(to: str) -> None:
        user = User.objects.filter(email=to).first()
        if not user:
            raise ValueError("등록된 이메일이 아닙니다.")
        if not user.has_usable_password():
            raise ValueError(
                "해당 계정은 소셜 로그인으로 가입된 계정입니다. 소셜 로그인을 이용해주세요."
            )

    return _send_code_common(
        purpose=EmailVerificationPurpose.PASSWORD_RESET,
        email=email,
        subject="[Studigo] 비밀번호 재설정 인증코드",
        precheck=precheck,
    )


def email_confirm_code(
    *,
    purpose: EmailVerificationPurpose,
    email: str,
    request_id: str,
    verification_code: str,
) -> ConfirmCodeResult:
    to = normalize_email(email)
    purpose_value = purpose.value

    lk = _lock_key(purpose_value, to, request_id)
    if cache.get(lk):
        raise ValueError("시도 제한 횟수를 초과했습니다. 잠시 뒤 다시 시도해주세요.")

    pk = _pending_key(purpose_value, to, request_id)
    cached_code = cache.get(pk)
    if not cached_code:
        raise ValueError("인증 요청이 없거나 만료되었습니다.")

    if not secrets.compare_digest(str(cached_code), str(verification_code)):
        fk = _failcnt_key(purpose_value, to, request_id)
        cnt = _safe_incr(fk, CODE_TTL)
        if cnt >= MAX_ATTEMPTS:
            cache.set(lk, "1", timeout=CODE_TTL)
            raise ValueError(
                "시도 제한 횟수를 초과했습니다. 잠시 뒤 다시 시도해주세요."
            )
        raise ValueError("인증코드가 유효하지 않습니다.")

    token = issue_verify_token(sub=to, purpose=purpose)

    cache.delete(_failcnt_key(purpose_value, to, request_id))
    cache.delete(lk)
    cache.delete(pk)

    expires = int(getattr(settings, "VERIFY_TOKEN_EXPIRES_SECONDS", 600))
    return ConfirmCodeResult(email_verify_token=token, expires_in=expires)
