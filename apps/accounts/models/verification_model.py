from django.db import models
from django.db.models import Q

from apps.core.enumeration.account_verification_enumeration import (
    VerificationPurpose,
    VerificationStatus,
)
from apps.core.models import VerificationTimeStampedModel


class Verification(VerificationTimeStampedModel):
    status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
    )
    target = models.CharField(
        max_length=150, help_text="EMAIL일 시 email 입력, PHONE일 시 phone 저장"
    )
    code = models.CharField(max_length=255)
    purpose = models.CharField(choices=VerificationPurpose.choices)

    class Meta:
        db_table = "verifications"
        constraints = [
            models.CheckConstraint(
                name="ck_verification_purpose_match_status",
                check=(
                    (
                        Q(status=VerificationStatus.EMAIL)
                        & Q(purpose__startswith="EMAIL_")
                    )
                    | (
                        Q(status=VerificationStatus.PHONE)
                        & Q(purpose__startswith="PHONE_")
                    )
                ),
            )
        ]
