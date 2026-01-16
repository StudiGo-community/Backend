from django.db import models

from apps.core.models import TimeStampedModel


class PostLike(TimeStampedModel):
    post = models.ForeignKey("Posts", on_delete=models.CASCADE)  # 게시글
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)  # 사용자

    class Meta:
        db_table = "post_likes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="unique_post_likes_user_post"
            )
        ]
        Indexes = [
            models.Index(fields=["user", "created_at"])  # 마이페이지 > 내가 좋아한 글
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.post}"
