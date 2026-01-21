from django.db import models


class EmailVerificationPurpose(models.TextChoices):
    SIGNUP = "SIGNUP"
    PASSWORD_RESET = "PASSWORD_RESET"
    # EMAIL_CHANGE = "EMAIL_CHANGE"


class PhoneVerificationPurpose(models.TextChoices):
    SIGNUP = "SIGNUP"
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_FINDING = "EMAIL_FINDING"
    # PHONE_CHANGE = "PHONE_CHANGE"
