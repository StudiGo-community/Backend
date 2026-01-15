from django.db import models


class PostImage(models.Model):
    post = models.ForeignKey("Posts", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=255)
    sort_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_image"
        constraints = [models.UniqueConstraint(fields=["post", "image_url"])]
        indexes = [
            models.Index(fields=["post", "sort_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.post} {self.image_url}"
