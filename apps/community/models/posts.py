from django.db import models

from apps.core.models import TimeStampedModel


class Posts(TimeStampedModel):
    class Category(models.TextChoices):
        TEST = "TEST", "DELE(델레) / 시험 대비"
        Travel = "Travel", "여행 & 현지 경험"
        Movie = "Movie", "영화 & 드라마"
        Free = "Free", "자유"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "공개"
        BLINDED = "BLINDED", "비공개"
        DELETED = "DELETED", "삭제"

    author = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="posts"
    )  # user ID

    title = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용
    category = models.CharField(
        choices=Category.choices, default=Category.Free
    )  # 카테고리 4개 중 선택 가능, 기본은 자유

    status = models.CharField(
        choices=Status.choices, default=Status.ACTIVE
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
            models.Index(fields=["status", "updated_at"]),
        ]

    def __str__(self) -> str:
        return f"[self.category] {self.title}"
