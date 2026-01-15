from django.db import models

from apps.chat.models import membership


class Message(models.Model):
    class Status(models.TextChoices):
        SENT = "SENT"
        DELETED_BY_ADMIN = "DELETED_BY_ADMIN"

    room = (
        models.ForeignKey("room", on_delete=models.CASCADE, related_name="message"),
    )  # 채팅방

    sender = models.ForeignKey(
        "membership", on_delete=models.CASCADE, related_name="message"
    )  # 메세지 보낸 사람의 ID

    content = models.TextField()

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.SENT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_message"
        indexes = [
            models.Index(
                fields=["room_id", "created_at"], name="idx_chat_room_created_at"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.sender} {self.room} {self.content}"
