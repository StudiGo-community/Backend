from django.db import models


class ReportStatus(models.TextChoices):
    PENDING = "PENDING", "진행중"
    RESOLVED = "RESOLVED", "승인"
    REJECTED = "REJECTED", "거부"


class PostCommentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "공개"
    BLINDED = "BLINDED", "비공개"
    DELETED = "DELETED", "삭제"


class PostCategory(models.TextChoices):
    RECRUIT = "RECRUIT", "모집 게시판"
    STUDY = "STUDY", "학습 게시판"
    FREE = "FREE", "자유 게시판"
