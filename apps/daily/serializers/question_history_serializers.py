from typing import Any

from rest_framework import serializers


class QuestionHistoryItemSerializer(serializers.Serializer[Any]):
    date = serializers.DateField()
    is_submitted = serializers.BooleanField()


class QuestionHistoryResponseSerializer(serializers.Serializer[Any]):
    results = QuestionHistoryItemSerializer(many=True)
