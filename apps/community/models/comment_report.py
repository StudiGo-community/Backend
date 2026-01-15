from django.db import models

from apps import accounts


class Status(models.TextChoices):
    PENDING = "PENDING", "진행중"
    RESOLVED = "RESOLVED", "승인"
    REJECTED = "REJECTED", "거부"


class CommentReport(models.Model):
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE)
    reporter = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    reason = models.CharField(max_length=100)
    status = models.CharField(default=Status.PENDING, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comment_report"
        constraints = [models.UniqueConstraint(fields=["comment", "reporter"])]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["comment", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reporter} {self.comment} {self.reason} {self.status}"
