from typing import Any

from rest_framework import serializers


class QuestionSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    prompt = serializers.CharField()


class DailyQuestionUnsolvedResponseSerializer(serializers.Serializer[Any]):
    question_date = serializers.DateField()
    daily_question_id = serializers.IntegerField()
    question = QuestionSerializer()
    expires_at = serializers.DateTimeField()


class DailyQuestionSolvedResponseSerializer(serializers.Serializer[Any]):
    date = serializers.DateField()
    explanation = serializers.CharField(allow_blank=True)
    answer_correct = serializers.CharField(allow_blank=True)
    answer_user = serializers.CharField(allow_blank=True)
    is_correct = serializers.BooleanField()
