from django.db import models


class EmailVerificationPurpose(models.TextChoices):
    SIGNUP = "SIGNUP", "회원가입"
    PASSWORD_RESET = "PASSWORD_RESET", "비밀번호 재설정"

class PhoneVerificationPurpose(models.TextChoices):
    SIGNUP = "SIGNUP", "회원가입"
    FIND_EMAIL = "FIND_EMAIL", "이메일 찾기"
    CHANGE_PHONE = "CHANGE_PHONE", "휴대폰 번호 변경"
