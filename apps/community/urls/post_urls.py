from django.urls import URLPattern, URLResolver, path

from apps.community.views.post_views import PostCreateListAPIView

urlpatterns: list[URLPattern | URLResolver] = [
    path("posts/", PostCreateListAPIView.as_view(), name="posts"),
]
