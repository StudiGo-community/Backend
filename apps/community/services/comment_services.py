from math import ceil
from typing import Any, Literal, TypedDict, cast

from django.db import transaction
from django.db.models import F, QuerySet
from rest_framework.generics import get_object_or_404

from apps.accounts.models import User
from apps.community.models.comments import Comment
from apps.community.models.posts import Post
from apps.core.choices.community_choices import PostCommentStatus

SortType = Literal["LATEST", "OLDEST"]


@transaction.atomic
def create_comment(*, post_id: int, author: User, content: str) -> Comment:
    post = get_object_or_404(Post, pk=post_id)

    comment: Comment = Comment.objects.create(  # type: ignore[attr-defined]
        post=post,
        author=author,
        content=content,
    )

    cast(Any, Post).objects.filter(pk=post.pk).update(
        comment_count=F("comment_count") + 1
    )

    return comment


@transaction.atomic
def delete_comment(*, comment_id: int, user: User) -> None:
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        status=PostCommentStatus.ACTIVE,
    )

    if comment.author != user:
        raise PermissionError("삭제 권한이 없습니다.")

    comment.status = PostCommentStatus.DELETED
    comment.save(update_fields=["status"])

    cast(Any, Post).objects.filter(pk=comment.post.pk).update(
        comment_count=F("comment_count") - 1
    )


class CommentPaginationResult(TypedDict):
    comments: list[Comment]
    page: int
    size: int
    total_count: int
    total_pages: int
    has_next: bool


def get_post_comments(
    *,
    post: Post,
    page: int,
    size: int,
    sort: SortType,
) -> CommentPaginationResult:
    queryset: QuerySet[Comment] = Comment.objects.filter(  # type: ignore[attr-defined]
        post=post,
        status=PostCommentStatus.ACTIVE,
    )

    if sort == "OLDEST":
        queryset = queryset.order_by("created_at")
    else:
        queryset = queryset.order_by("-created_at")

    total_count = queryset.count()
    total_pages = ceil(total_count / size) if total_count > 0 else 1

    offset = (page - 1) * size
    if offset >= total_count:
        return {
            "comments": [],
            "page": page,
            "size": size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": False,
        }
    comments: list[Comment] = list(queryset[offset : offset + size])

    return {
        "comments": comments,
        "page": page,
        "size": size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
    }
