from django.db import models

from apps.core.enumeration.community_enumerations import ReportStatus


class CommentReport(models.Model):
    comment = models.ForeignKey(
        "Comment", on_delete=models.CASCADE, related_name="reports"
    )
    reporter = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="reports"
    )
    reason = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10, default=ReportStatus.PENDING, choices=ReportStatus.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)

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
