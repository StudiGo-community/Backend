from django.db import models

from apps.core.choices.community_choices import PostCategory, PostCommentStatus
from apps.core.models import TimeStampedModel


class Post(TimeStampedModel):
    author = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, related_name="posts", null=True
    )  # user ID

    title = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용
    category = models.CharField(
        max_length=10, choices=PostCategory.choices, default=PostCategory.FREE
    )  # 카테고리 4개 중 선택 가능, 기본은 자유

    thumbnail_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=PostCommentStatus.choices,
        default=PostCommentStatus.ACTIVE,
    )  # 게시물 활성화 상태
    blinded_reason = models.CharField(
        max_length=100, null=True, blank=True
    )  # 게시글 블라인드 사유

    like_count = models.IntegerField(default=0)  # 좋아요 수
    comment_count = models.IntegerField(default=0)  # 댓글 수
    view_count = models.BigIntegerField(default=0)  # 조회 수

    class Meta:
        db_table = "posts"
        indexes = [
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.category}] {self.title}"
