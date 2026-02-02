from __future__ import annotations

from django.db import models

from apps.accounts.models import User
from apps.chat.models.message import Message
from apps.core.models import TimeStampedModel


class MessageReport(TimeStampedModel):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="reports"
    )
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_message_reports"
    )
    reason = models.CharField(max_length=200)

    class Meta:
        db_table = "chat_message_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["message", "reporter"],
                name="uq_msg_report_message_reporter",
            )
        ]
        indexes = [
            models.Index(fields=["message_id", "created_at"], name="idx_mr_msg_ct"),
            models.Index(fields=["reporter_id", "created_at"], name="idx_mr_rep_ct"),
        ]
