from django.db import models

from apps.core.enumeration.account_verification_enumeration import PhoneVerificationPurpose
from apps.core.models import VerificationTimeStampedModel


class PhoneVerification(VerificationTimeStampedModel):
    phone = models.CharField(max_length=30)
    code = models.CharField(max_length=255)
    purpose = models.CharField(choices=PhoneVerificationPurpose.choices)

    class Meta:
        db_table = "phone_verifications"
