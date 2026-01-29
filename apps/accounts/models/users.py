from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.core.enumeration.account_user_enumeration import (
    GenderChoices,
    SocialProviderChoices,
    UserRoleChoices,
    UserStatus,
)
from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager["User"]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        email = self.normalize_email(email).lower().strip()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str, **extra_fields: Any
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, TimeStampedModel):
    email = models.CharField(max_length=150, unique=True)
    nickname = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=10)
    gender = models.CharField(choices=GenderChoices.choices, max_length=1)
    phone = models.CharField(max_length=15)
    birthday = models.DateField(null=True, blank=True)
    profile_image_url = models.URLField(null=True, blank=True)
    status = models.CharField(
        choices=UserStatus.choices, max_length=12, default=UserStatus.ACTIVE
    )
    role = models.CharField(
        choices=UserRoleChoices.choices, max_length=20, default=UserRoleChoices.USER
    )

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False, null=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname", "name", "gender", "phone", "birthday"]

    class Meta:
        db_table = "users"


class OAuthAccount(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(choices=SocialProviderChoices.choices, max_length=12)
    provider_user_id = models.CharField(max_length=255)

    class Meta:
        db_table = "oauth_accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_user_id"],
                name="unique_oauth_provider_provider_user_id",
            )
        ]
        indexes = [
            models.Index(fields=["user"], name="idx_oauth_user"),
            models.Index(fields=["provider"], name="idx_oauth_provider"),
        ]
