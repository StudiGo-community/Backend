#!/bin/bash
set -euo pipefail

python manage.py shell <<'PY'
from django.db.models import Count
from apps.community.models.comments import Comment
from apps.community.models.post_likes import PostLike
from apps.community.models.posts import Post
from apps.core.choices.community_choices import PostCommentStatus

comment_rows = (
    Comment.objects.filter(status=PostCommentStatus.ACTIVE)
    .values("post_id")
    .annotate(cnt=Count("id"))
)
comment_map = {r["post_id"]: r["cnt"] for r in comment_rows}

like_rows = PostLike.objects.values("post_id").annotate(cnt=Count("id"))
like_map = {r["post_id"]: r["cnt"] for r in like_rows}

posts = list(Post.objects.all().only("id", "comment_count", "like_count"))
for p in posts:
    p.comment_count = comment_map.get(p.id, 0)
    p.like_count = like_map.get(p.id, 0)

Post.objects.bulk_update(posts, ["comment_count", "like_count"], batch_size=1000)
print(f"Done. Updated {len(posts)} posts.")
PY
