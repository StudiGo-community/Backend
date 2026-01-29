from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.daily.models.daily_question_submissions import DailyQuestionSubmission


class DailyQuestionSubmissionCreateSerializer(serializers.Serializer):
    submitted_answer_text = serializers.CharField(max_length=100, allow_blank=False)

    def validate_submitted_answer_text(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("제출할 정답은 공백일 수 없습니다.")
        return cleaned


class DailyQuestionSubmissionResponseSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source="daily_question.question_date", read_only=True)
    explanation = serializers.CharField(
        source="daily_question.question.explanation", read_only=True
    )
    answer_correct = serializers.CharField(
        source="daily_question.question.answer_text", read_only=True
    )
    answer_user = serializers.CharField(source="submitted_answer_text", read_only=True)

    class Meta:
        model = DailyQuestionSubmission
        fields = ["date", "explanation", "answer_correct", "answer_user", "is_correct"]

    def to_representation(self, instance: DailyQuestionSubmission) -> dict[str, Any]:
        # explanation / answer_text 가 null일 수도 있으니 안전하게 None -> "" 처리
        data = super().to_representation(instance)
        if data.get("explanation") is None:
            data["explanation"] = ""
        if data.get("answer_correct") is None:
            data["answer_correct"] = ""
        if data.get("answer_user") is None:
            data["answer_user"] = ""
        return data