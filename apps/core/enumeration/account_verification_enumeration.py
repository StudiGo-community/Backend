from django.db import models


class VerificationStatus(models.TextChoices):
    EMAIL = "EMAIL", "email"
    PHONE = "PHONE", "phone"


class VerificationPurpose(models.TextChoices):
    EMAIL_SIGNUP = "EMAIL_SIGNUP", "email_signup"
    EMAIL_PASSWORD_RESET = "EMAIL_PASSWORD_RESET", "email_password_reset"
    PHONE_SIGNUP = "PHONE_SIGNUP", "phone_signup"
    PHONE_PASSWORD_RESET = "PHONE_PASSWORD_RESET", "phone_password_reset"
