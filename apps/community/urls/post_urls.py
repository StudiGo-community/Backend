from django.urls import URLPattern, URLResolver, path

from apps.community.views.post_views import (
    PostCreateListAPIView,
    PostDetailAPIView,
    PostLikeView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("posts/", PostCreateListAPIView.as_view(), name="posts"),
    path("posts/<int:post_id>", PostDetailAPIView.as_view(), name="post_detail"),
    path("posts/<int:post_id>/like/", PostLikeView.as_view(), name="post_like"),
]
