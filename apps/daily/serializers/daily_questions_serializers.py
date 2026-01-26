from typing import Any

from rest_framework import serializers


class QuestionSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    prompt = serializers.CharField()


class DailyQuestionTodayResponseSerializer(serializers.Serializer[Any]):
    question_date = serializers.DateField()
    daily_question_id = serializers.IntegerField()
    question = QuestionSerializer()
    expires_at = serializers.DateTimeField()
