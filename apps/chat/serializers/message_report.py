from __future__ import annotations

from typing import Any
from rest_framework import serializers

class MessageReportCreateSerializer(serializers.Serializer[Any]):
    reason = serializers.CharField(max_length=200)

class MessageReportCreateResponseSerializer(serializers.Serializer[Any]):
    message = serializers.CharField()
