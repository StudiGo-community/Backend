from django.db import models

from apps.core.enumeration.community_enumerations import ReportStatus
from apps.core.models import BaseReport


class PostReport(BaseReport):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="post_reports",
    )  # 게시글 id

    class Meta:
        db_table = "post_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["post", "reporter"],
                name="unique_post_reports_post_reporter",
            )
        ]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["reporter", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reporter} {self.post} {self.reason} {self.status}"
