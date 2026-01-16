from django.db import models


class PostReport(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "진행중"
        RESOLVED = "RESOLVED", "승인"
        REJECTED = "REJECTED", "거부"

    post = models.ForeignKey("Posts", on_delete=models.CASCADE)  # 게시글 id
    reporter = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE
    )  # 차단 대상 id
    reason = models.CharField(max_length=100)  # 차단 사유
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )  # 징행 상태

    class Meta:
        db_table = "post_report"
        constraints = [models.UniqueConstraint(fields=["post", "reporter"])]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["reporter", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reporter} {self.post} {self.reason} {self.status}"
