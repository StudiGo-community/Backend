from django.urls import URLPattern, URLResolver

from apps.accounts.urls.auth_urls import urlpatterns as auth_urls
from apps.accounts.urls.mypage_profile_urls import urlpatterns as mypage_profile_urls
from apps.accounts.urls.oauth_urls import urlpatterns as oauth_urls

app_name = "accounts"

urlpatterns: list[URLPattern | URLResolver] = [
    *auth_urls,
    *oauth_urls,
    *mypage_profile_urls,
]
