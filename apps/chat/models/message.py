from django.db import models

from apps.core.models import TimeStampedModel


class Message(TimeStampedModel):
    class Status(models.TextChoices):
        SENT = "SENT"
        DELETED_BY_ADMIN = "DELETED_BY_ADMIN"

    # 채팅방
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="message")

    sender = models.ForeignKey(
        "Membership", on_delete=models.CASCADE, related_name="message"
    )  # 메세지 보낸 사람의 ID

    content = models.TextField()

    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.SENT
    )

    class Meta:
        db_table = "chat_message"
        indexes = [
            models.Index(
                fields=["room", "created_at"], name="idx_chat_room_created_at"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.sender} {self.room} {self.content}"
