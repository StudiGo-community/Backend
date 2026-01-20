from typing import Any, Optional, cast

from django.db import transaction
from django.db.models import Exists, F, OuterRef, Prefetch, Q

from apps.community.models.comments import Comment
from apps.community.models.post_images import PostImage
from apps.community.models.post_likes import PostLike
from apps.community.models.posts import Post
from apps.core.enumeration.community_enumerations import PostCategory, PostCommentStatus


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


def get_post_list(
    *,
    user: Any,
    category: Optional[str],
    sort: str,
    keyword: Optional[str],
    search_field: str,
) -> Any:
    post_queryset = (
        cast(Any, Post)
        .objects.filter(status=PostCommentStatus.ACTIVE)
        .select_related("author")
        .prefetch_related("images")
    )

    # category 필터 (미지정시 전체 조회)
    if category:
        allowed_category = {choice for choice, _ in PostCategory.choices}
        if category in allowed_category:
            post_queryset = post_queryset.filter(category=category)

    # 검색
    if keyword:
        keyword = keyword.strip()
        if keyword:
            if search_field == "title":
                post_queryset = post_queryset.filter(title__icontains=keyword)
            elif search_field == "content":
                post_queryset = post_queryset.filter(content__icontains=keyword)
            else:  # all
                post_queryset = post_queryset.filter(
                    Q(title__icontains=keyword) | Q(content__icontains=keyword)
                )

    # 정렬
    if sort == "oldest":
        post_queryset = post_queryset.order_by("created_at")
    elif sort == "popular":
        post_queryset = post_queryset.order_by("-like_count", "-created_at")
    else:  # 기본 최신순 정렬
        post_queryset = post_queryset.order_by("-created_at")

    if getattr(user, "is_authenticated", False):
        liked_subquery = cast(Any, PostLike).objects.filter(
            user=user, post=OuterRef("pk")
        )
        post_queryset = post_queryset.annotate(is_liked=Exists(liked_subquery))
    else:
        post_queryset = post_queryset.annotate(
            is_liked=Exists(cast(Any, PostLike).objects.none())
        )

    return post_queryset


@transaction.atomic
def get_post_detail(*, user: Any, post_id: int) -> Any | None:

    # 게시글 조회수 증가
    updated = (
        cast(Any, Post)
        .objects.filter(
            pk=post_id,
            status=PostCommentStatus.ACTIVE,
        )
        .update(view_count=F("view_count") + 1)
    )

    if updated == 0:
        return None

    # 좋아요 여부
    if getattr(user, "is_authenticated", False):
        liked_subquery = cast(Any, PostLike).objects.filter(
            user=user,
            post=OuterRef("pk"),
        )
        queryset = cast(Any, Post).objects.annotate(is_liked=Exists(liked_subquery))
    else:
        queryset = cast(Any, Post).objects.annotate(
            is_liked=Exists(cast(Any, PostLike).objects.none())
        )

    # 댓글 불러오기 (상태가 ACTIVE인 것만)
    comment_queryset = (
        cast(Any, Comment)
        .objects.filter(status=PostCommentStatus.ACTIVE)
        .select_related("author")
        .order_by("created_at")
    )

    post = (
        queryset.filter(pk=post_id, status=PostCommentStatus.ACTIVE)
        .select_related("author")
        .prefetch_related("images")
        .prefetch_related(Prefetch("comments", queryset=comment_queryset))
        .get()
    )

    return post
