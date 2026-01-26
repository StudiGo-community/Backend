from django.db import models

from apps.core.models import TimeStampedModel


class Question(TimeStampedModel):
    title = models.CharField(max_length=100, verbose_name="문제 제목")

    description = models.TextField(null=True, blank=True, verbose_name="문제 설명")

    prompt = models.TextField(verbose_name="문제 내용")

    answer_text = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="빈칸 정답"
    )

    explanation = models.TextField(null=True, blank=True, verbose_name="해설")

    is_active = models.BooleanField(default=True, verbose_name="활성 여부")

    class Meta:
        db_table = "questions"
        verbose_name = "문제"
        verbose_name_plural = "문제"

    def __str__(self) -> str:
        return self.title
