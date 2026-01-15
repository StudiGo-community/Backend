from django.db import models

from apps.core.models import TimeStampedModel


class PostImage(TimeStampedModel):
    post = models.ForeignKey("Posts", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=255)
    sort_order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "post_image"
        indexes = [
            models.Index(fields=["post", "sort_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.post} {self.image_url}"
