from django.db import models

from apps.core.enumeration.account_user_enumeration import VerificationPurpose
from apps.core.models import VerificationTimeStampedModel


class PhoneVerification(VerificationTimeStampedModel):
    phone = models.CharField(max_length=30)
    code = models.CharField(max_length=255)
    purpose = models.CharField(
        choices=VerificationPurpose.choices, default=VerificationPurpose.SIGNUP
    )

    class Meta:
        db_table = "phone_verification"
