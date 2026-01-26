from django.db import models

from apps.core.enumeration.community_enumerations import ReportStatus
from apps.core.models import BaseReport


class CommentReport(BaseReport):
    comment = models.ForeignKey(
        "Comment",
        on_delete=models.CASCADE,
        related_name="reports",
    )

    class Meta:
        db_table = "comment_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["comment", "reporter"],
                name="unique_comment_reports_comment_reporter",
            )
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["comment", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reporter} {self.comment} {self.reason} {self.status}"
