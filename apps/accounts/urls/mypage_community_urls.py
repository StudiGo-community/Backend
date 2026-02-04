from django.urls import URLPattern, URLResolver, path

from apps.accounts.views.mypage_community_views import (
    MyCommentsAPIView,
    MyLikedPostsAPIView,
    MyPostsAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("users/me/profile/posts", MyPostsAPIView.as_view(), name="my-posts"),
    path("users/me/profile/comments", MyCommentsAPIView.as_view(), name="my-comments"),
    path("users/me/profile/liked-posts", MyLikedPostsAPIView.as_view(), name="my-liked-posts"),
]
