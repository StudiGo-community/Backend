from django.db import models

# Create your models here.


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
