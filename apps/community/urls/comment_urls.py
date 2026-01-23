from django.urls import path

from apps.community.views.comment_views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
)

urlpatterns = [
    path("posts/<int:post_id>/comments", CommentCreateAPIView.as_view(), name="comment_create"),
]
