from django.db import models

from apps.core.enumeration.account_verification_enumeration import EmailVerificationPurpose
from apps.core.models import VerificationTimeStampedModel


class EmailVerification(VerificationTimeStampedModel):
    email = models.CharField(max_length=150)
    code = models.CharField(max_length=255)
    purpose = models.CharField(choices=EmailVerificationPurpose.choices)

    class Meta:
        db_table = "email_verifications"
