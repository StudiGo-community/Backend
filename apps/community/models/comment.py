from django.db import models

from apps.core.models import TimeStampedModel


class Comment(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "공개"
        BLINDED = "BLINDED", "비공개"
        DELETED = "DELETED", "삭제"

    post = models.ForeignKey("Posts", on_delete=models.CASCADE)  # 게시글 id
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)  # 유저 id
    content = models.TextField()  # 댓글 내용

    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.ACTIVE
    )  # 댓글 상태
    blinded_reason = models.CharField(
        max_length=100, null=True, blank=True
    )  # 댓글 사유
    blinded_at = models.DateTimeField(null=True, blank=True)  # 댓글 시간

    class Meta:
        db_table = "comments"
        Indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.author} {self.post}"
