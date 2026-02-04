from __future__ import annotations

from django.db import models

from apps.chat.models.message import Message
from apps.core.models import BaseReport


class MessageReport(BaseReport):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    class Meta:
        db_table = "chat_message_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["message", "reporter"],
                name="uq_message_reporter",
            )
        ]
        indexes = [
            models.Index(fields=["message"]),
            models.Index(fields=["status"]),
        ]

        def __str__(self) -> str:
            return f"message={self.message_id} report={self.reportot_id}"
