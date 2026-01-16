from django.db import models

from apps.core.enumeration.community_enumerations import ReportStatus


class PostReport(models.Model):
    post = models.ForeignKey(
        "Posts", on_delete=models.CASCADE, related_name="reports"
    )  # 게시글 id
    reporter = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="reports"
    )  # 차단 대상 id
    reason = models.CharField(max_length=100)  # 차단 사유
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=ReportStatus.choices, default=ReportStatus.PENDING
    )  # 징행 상태

    class Meta:
        db_table = "post_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["post", "reporter"], name="unique_post_reports_post_reporter"
            )
        ]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["reporter", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reporter} {self.post} {self.reason} {self.status}"
