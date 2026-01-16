from typing import Any, Optional, cast

from django.db import transaction

from apps.community.models.post_images import PostImage
from apps.community.models.posts import Post


@transaction.atomic
def create_post(
    *,
    author: Any,
    title: str,
    content: str,
    category: str,
    images: list[dict[str, str]] | None,
    thumbnail_url: Optional[str] = None,
) -> Any:
    post = cast(Any, Post).objects.create(
        author=author,
        title=title,
        content=content,
        category=category,
        thumbnail_url=thumbnail_url,
    )

    if images:
        cast(Any, PostImage).objects.bulk_create(
            [
                PostImage(
                    post=post,
                    image_url=img["url"],
                    sort_order=img["order"],
                )
                for img in images
            ]
        )

    return (
        cast(Any, Post)
        .objects.filter(pk=post.pk)
        .select_related("author")
        .prefetch_related("images")
        .get()
    )
