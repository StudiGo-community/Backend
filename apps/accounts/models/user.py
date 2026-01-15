from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from apps.accounts.models.user_enumerate import (
    GenderChoices,
    UserRoleChoices,
    UserStatus,
)
from apps.core.models import TimeStampedModel


class User(AbstractBaseUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=10)
    gender = models.CharField(choices=GenderChoices.choices, max_length=1)
    phone = models.CharField(max_length=15)
    birthday = models.DateField()
    profile_image_url = models.CharField(max_length=255)  # URLField?
    status = models.CharField(choices=UserStatus.choices, max_length=12)
    role = models.CharField(
        choices=UserRoleChoices.choices, max_length=20, default=UserRoleChoices.USER
    )
