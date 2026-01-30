from django.db import models

from apps.core.models import TimeStampedModel


class Language(models.TextChoices):
    KO = "ko"
    ES = "es"


class Translation(TimeStampedModel):

    message = models.ForeignKey(
        "Message", on_delete=models.CASCADE, related_name="translations"
    )  # 번역할 메세지 id
    target_language = models.CharField(
        choices=Language, default=Language.KO
    )  # 번역할 언어 (ko or es)
    translated_text = models.TextField()  # 번역 완료한 메세지

    class Meta:
        db_table = "chat_translation"
        constraints = [
            models.UniqueConstraint(
                fields=["message", "target_language"],
                name="uq_chat_translation_message_target_lang",
            )
        ]
        indexes = [
            models.Index(fields=["message", "target_language"]),
        ]

    def __str__(self) -> str:
        return f"{self.target_language} {self.translated_text}"
