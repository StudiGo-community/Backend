from django.db import models

from apps.core.models import TimeStampedModel
from apps.daily.models.questions import Question


class DailyQuestion(TimeStampedModel):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="daily_questions",
        verbose_name="문제"
    )

    question_date = models.DateField(
        unique=True,
        verbose_name="문제 날짜",
        help_text="해당 날짜에 제공되는 오늘의 문제 (하루 1문제)"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="활성 여부"
    )

    class Meta:
        db_table = "daily_questions"
        verbose_name = "오늘의 문제"
        verbose_name_plural = "오늘의 문제"
        constraints = [
            models.UniqueConstraint(
                fields=["question_date"],
                name="uk_daily_questions_date"
            )
        ]

    def __str__(self) -> str:
        return f"{self.question_date} - {self.question.title}"