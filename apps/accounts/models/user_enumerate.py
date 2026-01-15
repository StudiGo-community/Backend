from django.db import models


class GenderChoices(models.TextChoices):
    MALE = "M"
    FEMALE = "F"


class UserStatus(models.TextChoices):
    ACTIVE = ("ACTIVE",)
    DEACTIVATED = "DEACTIVATED"
    BANNED = "BANNED"
    DORMANT = "DORMANT"


class UserRoleChoices(models.TextChoices):
    ADMIN = "ADMIN"
    USER = "USER"
    INSTRUCTOR = "INSTRUCTOR"


class SocialProviderChoices(models.TextChoices):
    G = "GOOGLE"
    K = "KAKAO"

class VerificationPurpose(models.TextChoices):
    SIGNUP = "SIGNUP"
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_CHANGE = "EMAIL_CHANGE"
    PHONE_CHANGE = "PHONE_CHANGE"