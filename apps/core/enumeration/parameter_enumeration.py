from django.db import models


class Sort(models.TextChoices):
    LATEST = "latest", "최신순"
    OLDEST = "oldest", "오래된순"
    POPULAR = "popular", "인기순"


class SearchField(models.TextChoices):
    TITLE = "title", "제목"
    CONTENT = "content", "내용"
    ALL = "all", "전체"
