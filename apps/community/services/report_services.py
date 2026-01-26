from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.community.models.comment_reports import CommentReport
from apps.community.models.comments import Comment
from apps.community.models.post_reports import PostReport
from apps.community.models.posts import Post


@transaction.atomic
def create_post_report(*, post: Post, reporter: User, reason: str) -> PostReport:
    if PostReport.objects.filter(post=post, reporter=reporter).exists():
        raise ValidationError({"detail" : "이미 신고한 게시글 입니다."})

    report = PostReport.objects.create(
        post=post,
        reporter=reporter,
        reason=reason,
    )
    return report

@transaction.atomic
def create_comment_report(*, comment: Comment, reporter: User, reason: str) -> CommentReport:
    if CommentReport.objects.filter(comment=comment, reporter=reporter).exists():
        raise ValidationError({"detail" : "이미 신고한 댓글 입니다."})

    report = CommentReport.objects.create(
        comment=comment,
        reporter=reporter,
        reason=reason,
    )
    return report