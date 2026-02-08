from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.community.models.comments import Comment
from apps.community.models.posts import Post
from apps.core.choices.community_choices import PostCommentStatus

"""마이페이지 체크박스 삭제용 (posts/comments 공용)."""


class BulkDeleteSerializer(serializers.Serializer[dict[str, Any]]):

    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text="삭제할 ID 목록",
    )


class _PreviewMixin:
    @staticmethod
    def _make_preview(text: str, *, max_length: int = 100) -> str:
        cleaned = (text or "").strip().replace("\n", " ")
        if len(cleaned) <= max_length:
            return cleaned
        return cleaned[:max_length].rstrip() + "…"


class MyPostListItemSerializer(_PreviewMixin, serializers.ModelSerializer[Post]):
    content_preview = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content_preview",
            "view_count",
            "comment_count",
            "like_count",
            "created_at",
        )

    def get_content_preview(self, post: Post) -> str:
        return self._make_preview(post.content, max_length=100)


class MyCommentListItemSerializer(_PreviewMixin, serializers.ModelSerializer[Comment]):
    content_preview = serializers.SerializerMethodField()
    post_id = serializers.IntegerField(source="post.id", read_only=True)
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "post_id",
            "post_title",
            "content_preview",
            "created_at",
            "is_deleted",
        )

    def get_content_preview(self, comment: Comment) -> str:
        return self._make_preview(comment.content, max_length=100)

    def get_is_deleted(self, comment: Comment) -> bool:
        # 원본 게시글이 삭제된 경우
        return getattr(comment.post, "status", None) == PostCommentStatus.DELETED

    def get_post_title(self, comment: Comment) -> str:
        if getattr(comment.post, "status", None) == PostCommentStatus.DELETED:
            return "삭제된 게시글입니다."
        return getattr(comment.post, "title", "")

class MyLikedPostListItemSerializer(_PreviewMixin, serializers.ModelSerializer[Post]):
    title = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content_preview",
            "view_count",
            "comment_count",
            "like_count",
            "created_at",
            "is_deleted",
        )

    def get_is_deleted(self, post: Post) -> bool:
        return post.status == PostCommentStatus.DELETED

    def get_title(self, post: Post) -> str:
        if post.status == PostCommentStatus.DELETED:
            return "삭제된 게시글입니다."
        return post.title

    def get_content_preview(self, post: Post) -> str:
        if post.status == PostCommentStatus.DELETED:
            return ""
        return self._make_preview(post.content, max_length=100)
