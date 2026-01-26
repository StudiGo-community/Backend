from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from apps.community.models.comment_reports import CommentReport
from apps.community.models.comments import Comment
from apps.community.models.post_reports import PostReport
from apps.community.models.posts import Post


@transaction.atomic
def create_post_report(*, post_id: int, reporter: User, reason: str) -> PostReport:
    # 게시글 존재 확인
    post = get_object_or_404(Post, pk=post_id)
    report: PostReport = PostReport.objects.create(  # type: ignore[attr-defined]
        post=post,
        reporter=reporter,
        reason=reason,
    )
    return report


@transaction.atomic
def create_comment_report(
    *, post_id: int, comment_id: int, reporter: User, reason: str
) -> CommentReport:
    # 게시글 존재 확인
    post = get_object_or_404(Post, pk=post_id)

    # 댓글 존재 + 게시글 소속 확인
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    report: CommentReport = CommentReport.objects.create(  # type: ignore[attr-defined]
        comment=comment,
        reporter=reporter,
        reason=reason,
    )
    return report
