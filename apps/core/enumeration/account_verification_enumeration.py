from django.db import models


class EmailVerificationPurpose(models.TextChoices):
    SIGNUP = "SIGNUP", "회원가입"
    PASSWORD_RESET = "PASSWORD_RESET", "비밀번호 재설정"
