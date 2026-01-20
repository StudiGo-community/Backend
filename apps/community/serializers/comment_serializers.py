import re

from rest_framework import serializers

from apps.community.models.comments import Comment
from apps.community.serializers.common_serializers import AuthorSerializer

MENTION_REGEX = re.compile(r"@([A-Za-z0-9_.가-힣]{1,30})")


class CommentResponseSerializer(serializers.ModelSerializer[Comment]):
    author = AuthorSerializer(read_only=True)
    tagged_nicknames = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
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
