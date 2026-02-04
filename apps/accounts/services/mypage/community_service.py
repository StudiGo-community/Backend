from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any, Literal, TypedDict, cast

from django.db.models import F, QuerySet
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request

from apps.accounts.models import User
from apps.community.models.comments import Comment
from apps.community.models.posts import Post
from apps.core.choices.community_choices import PostCommentStatus

SortLatestOldest = Literal["latest", "oldest"]


class PaginationDict(TypedDict):
    current_page: int
    total_pages: int
    total_count: int
    has_next: bool
    has_previous: bool


class PaginatedResult(TypedDict):
    items: list[Any]
    pagination: PaginationDict


@dataclass
class DeleteResult:
    deleted_count: int


class MyPageCommunityService:
    """마이페이지 > 커뮤니티 관련 기능(내 글/댓글/좋아요 목록)."""

    @staticmethod
    def get_authenticated_user(request: Request) -> User:
        user = request.user
        if not getattr(user, "is_authenticated", False):
            raise NotAuthenticated()
        return cast(User, user)

    @staticmethod
    def _paginate_queryset(
        queryset: QuerySet[Any], *, page: int, size: int
    ) -> PaginatedResult:
        safe_page = page if page > 0 else 1
        safe_size = size if size > 0 else 10

        total_count = queryset.count()
        total_pages = ceil(total_count / safe_size) if total_count > 0 else 0

        offset = (safe_page - 1) * safe_size
        if total_count == 0 or offset >= total_count:
            items: list[Any] = []
        else:
            items = list(queryset[offset : offset + safe_size])

        has_next = safe_page < total_pages
        has_previous = safe_page > 1 and total_pages > 0

        return {
            "items": items,
            "pagination": {
                "current_page": safe_page,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": has_next,
                "has_previous": has_previous,
            },
        }

    def get_my_posts(
        self, *, user: User, page: int, size: int, sort: SortLatestOldest
    ) -> PaginatedResult:
        queryset = Post.objects.filter(  # type: ignore[attr-defined]
            author=user,
            status__in=[PostCommentStatus.ACTIVE, PostCommentStatus.BLINDED],
        )

        queryset = (
            queryset.order_by("created_at")
            if sort == "oldest"
            else queryset.order_by("-created_at")
        )
        return self._paginate_queryset(queryset, page=page, size=size)

    def delete_my_posts(self, *, user: User, post_ids: list[int]) -> DeleteResult:
        deleted_count = Post.objects.filter(  # type: ignore[attr-defined]
            author=user,
            id__in=post_ids,
            status__in=[PostCommentStatus.ACTIVE, PostCommentStatus.BLINDED],
        ).update(status=PostCommentStatus.DELETED)
        return DeleteResult(deleted_count=deleted_count)

    def get_my_comments(
        self, *, user: User, page: int, size: int, sort: SortLatestOldest
    ) -> PaginatedResult:
        queryset = Comment.objects.filter(  # type: ignore[attr-defined]
            author=user,
            status__in=[PostCommentStatus.ACTIVE, PostCommentStatus.BLINDED],
        ).select_related("post")

        queryset = (
            queryset.order_by("created_at")
            if sort == "oldest"
            else queryset.order_by("-created_at")
        )
        return self._paginate_queryset(queryset, page=page, size=size)

    def delete_my_comments(self, *, user: User, comment_ids: list[int]) -> DeleteResult:
        deleted_count = Comment.objects.filter(  # type: ignore[attr-defined]
            author=user,
            id__in=comment_ids,
            status__in=[PostCommentStatus.ACTIVE, PostCommentStatus.BLINDED],
        ).update(status=PostCommentStatus.DELETED)
        return DeleteResult(deleted_count=deleted_count)

    def get_my_liked_posts(
        self, *, user: User, page: int, size: int, sort: SortLatestOldest
    ) -> PaginatedResult:
        queryset = Post.objects.filter(  # type: ignore[attr-defined]
            likes__user=user,
        ).annotate(liked_at=F("likes__created_at"))

        # 기본: 좋아요한 최신순
        queryset = (
            queryset.order_by("liked_at", "-created_at")
            if sort == "oldest"
            else queryset.order_by("-liked_at", "-created_at")
        )
        return self._paginate_queryset(queryset, page=page, size=size)
