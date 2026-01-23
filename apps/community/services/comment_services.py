from django.db import transaction
from rest_framework.generics import get_object_or_404

from apps.community.models.comments import Comment
from apps.community.models.posts import Post
from apps.core.enumeration.community_enumerations import PostCommentStatus


@transaction.atomic
def create_comment(*, post_id: int, author, content: str) -> Comment:
    post = get_object_or_404(Post, pk=post_id)

    return Comment.objects.create(
        post=post,
        author=author,
        content=content,
    )


@transaction.atomic
def delete_comment(*, comment_id: int, user) -> None:
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        status=PostCommentStatus.ACTIVE,
    )

    if comment.author != user:
        raise PermissionError("삭제 권한이 없습니다.")

    comment.status = PostCommentStatus.DELETED
    comment.save(update_fields=["status"])