from typing import Any

from rest_framework import serializers

from apps.accounts.models.users import User
from apps.core.enumeration.account_verification_enumeration import (
    EmailVerificationPurpose,
    PhoneVerificationPurpose
)
from apps.accounts.serializers.base import BaseMixin

# class EmailSendCodeSerializer(serializers.Serializer, BaseMixin):