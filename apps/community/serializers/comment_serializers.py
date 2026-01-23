import re

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.community.models.comments import Comment
from apps.community.models.posts import Post
from apps.community.serializers.common_serializers import AuthorSerializer
from apps.core.enumeration.community_enumerations import PostCommentStatus

MENTION_REGEX = re.compile(r"@([A-Za-z0-9_.가-힣]{1,30})")


class CommentResponseSerializer(serializers.ModelSerializer[Comment]):
    author = AuthorSerializer(read_only=True)
    tagged_nicknames = serializers.SerializerMethodField()
    post_id = serializers.IntegerField(source="post.id", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "post_id",
            "author",
            "content",
            "tagged_nicknames",
            "created_at",
        )

    def get_tagged_nicknames(self, obj: Comment) -> list[str]:
        found = MENTION_REGEX.findall(obj.content or "")

        # 중복 제거 + 순서 유지
        seen: set[str] = set()
        result: list[str] = []
        for nick in found:
            if nick not in seen:
                seen.add(nick)
                result.append(nick)
        return result


class CommentCreateSerializer(serializers.Serializer[Comment]):
    content = serializers.CharField()
