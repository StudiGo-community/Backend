from django.urls import URLPattern, URLResolver

from apps.community.urls.comment_urls import urlpatterns as comment_urls
from apps.community.urls.post_urls import urlpatterns as post_urls

# from apps.community.urls.like_urls import urlpatterns as like_urls
# from apps.community.urls.report_urls import urlpatterns as report_urls

app_name = "community"

urlpatterns: list[URLPattern | URLResolver] = [
    *post_urls,
    *comment_urls,
    # *like_urls,
    # *report_urls,
]
