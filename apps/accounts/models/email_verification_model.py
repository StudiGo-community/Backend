from django.db import models

from apps.core.enumeration.account_verification_enumeration import VerificationPurpose
from apps.core.models import VerificationTimeStampedModel


class EmailVerification(VerificationTimeStampedModel):
    email = models.CharField(max_length=150)
    code = models.CharField(max_length=255)
    purpose = models.CharField(
        choices=VerificationPurpose.choices,
        default=VerificationPurpose.EMAIL_VERIFICATION,
    )

    class Meta:
        db_table = "email_verifications"
