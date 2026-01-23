from django.urls import path

from apps.community.views.comment_views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
    CommentListAPIView,
)

urlpatterns = [
    path(
        "posts/<int:post_id>/comments",
        CommentCreateAPIView.as_view(),
        name="comment_create",
    ),
    path(
        "posts/<int:post_id>/comments/<int:comment_id>",
        CommentDeleteAPIView.as_view(),
        name="comment_delete",
    ),
    path(
        "posts/<int:post_id>/comments/",
        CommentListAPIView.as_view(),
        name="comments_list",
    ),
]
