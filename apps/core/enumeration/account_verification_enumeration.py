from django.db import models

class VerificationPurpose(models.TextChoices):
    SIGNUP = "SIGNUP"
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_CHANGE = "EMAIL_CHANGE"
    PHONE_CHANGE = "PHONE_CHANGE"
