from django.db import models


class Translation(models.Model):
    message = models.ForeignKey("Message", on_delete=models.CASCADE)  # 번역할 메세지 id
    target_language = models.CharField(max_length=10)  # 번역할 언어 (ko or es)
    translated_text = models.TextField()  # 번역 완료한 메세지
    created_at = models.DateTimeField(auto_now_add=True)  # 번역된 시각

    class Meta:
        db_table = "chat_translation"
        constraints = [models.UniqueConstraint(fields=["message", "target_language"])]
        indexes = [
            models.Index(fields=["message", "target_language"]),
        ]

    def __str__(self) -> str:
        return f"{self.target_language} {self.translated_text}"
