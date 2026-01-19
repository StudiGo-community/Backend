from django.urls import URLPattern, URLResolver, path

from apps.community.views.post_views import PostCreateAPIView

urlpatterns: list[URLPattern | URLResolver] = [
    path("posts", PostCreateAPIView.as_view(), name="post_create"),
]
