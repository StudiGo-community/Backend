from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.daily.models.daily_questions import DailyQuestion


class DailyQuestionSubmission(TimeStampedModel):
    """
    로그인 사용자가 '오늘의 문제'를 제출한 기록 (사용자당 1일 1회)
    """

    daily_question: models.ForeignKey[DailyQuestion] = models.ForeignKey(
        DailyQuestion,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="오늘의 문제",
    )

    user: models.ForeignKey[settings.AUTH_USER_MODEL] = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_question_submissions",
        verbose_name="사용자",
    )

    submitted_answer_text: Optional[str] = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="제출한 답변",
    )

    is_correct: bool = models.BooleanField(
        default=False,
        verbose_name="정답 여부",
        help_text="정답=True, 오답=False",
    )

    class Meta:
        db_table = "daily_question_submissions"
        verbose_name = "일일 문제 제출"
        verbose_name_plural = "일일 문제 제출"
        constraints = [
            models.UniqueConstraint(
                fields=["daily_question", "user"],
                name="uk_daily_question_submission_user",
            )
        ]

    def __str__(self) -> str:
        return (
            "DailyQuestionSubmission("
            f"user_id={self.user_id}, date={self.daily_question.question_date}"
            ")"
        )