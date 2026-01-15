from django.conf import settings
from django.db import models

from apps.chat.models import room


class Membership(models.Model):
    room = models.ForeignKey(
        "room", on_delete=models.CASCADE, related_name="membership", db_index=True
    )  # 방 ID
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membership",
        db_index=True,
    )  # user ID
    joined_at = models.DateTimeField(auto_now_add=True)  # 채팅방 입장 시각
    left_at = models.DateTimeField(null=True, blank=True)  # 퇴장시각

    class Meta:
        db_table = "chat_membership"
        constraints = [
            models.UniqueConstraint(fields=["room", "user"], name="unique_membership")
        ]
        indexes = [
            models.Index(fields=["user", "joined_at"], name="idx_chat_user_joined_at"),
        ]

    def __str__(self) -> str:
        status = "IN" if self.left_at is None else "OUT"
        return f"{self.user} {status} {self.room}"
