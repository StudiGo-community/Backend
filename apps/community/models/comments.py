from django.db import models

from apps.core.choices.community_choices import PostCommentStatus
from apps.core.models import TimeStampedModel


class Comment(TimeStampedModel):

    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="comments"
    )  # 게시글 id
    author = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="comments"
    )  # 유저 id
    content = models.TextField()  # 댓글 내용

    status = models.CharField(
        choices=PostCommentStatus.choices, default=PostCommentStatus.ACTIVE
    )  # 댓글 상태
    blinded_reason = models.CharField(
        max_length=100, null=True, blank=True
    )  # 댓글 사유
    blinded_at = models.DateTimeField(null=True, blank=True)  # 댓글 시간

    class Meta:
        db_table = "comments"
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.author} {self.post}"
