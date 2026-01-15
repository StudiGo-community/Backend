from django.db import models

from apps.accounts.models.user_enumerate import VerificationPurpose
from apps.core.models import VerificationTimeStampedModel


class EmailVerification(VerificationTimeStampedModel):
    email = models.CharField(max_length=30)
    code = models.CharField(max_length=255)
    purpose = models.CharField(
        choices=VerificationPurpose.choices, default=VerificationPurpose.SIGNUP
    )

    class Meta:
        db_table = "email_verification"
