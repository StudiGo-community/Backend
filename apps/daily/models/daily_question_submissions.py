from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.daily.models.daily_questions import DailyQuestion


class DailyQuestionSubmission(TimeStampedModel):
    daily_question = models.ForeignKey(
        DailyQuestion,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="오늘의 문제",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_question_submissions",
        verbose_name="사용자",
    )

    submitted_answer_text = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="제출한 답변",
    )

    is_correct = models.BooleanField(
        default=False,
        verbose_name="정답 여부",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["daily_question", "user"],
                name="uk_daily_question_submission_user",
            )
        ]

    def __str__(self) -> str:
        return f"{self.pk}"
