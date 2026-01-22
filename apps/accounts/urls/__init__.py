from django.urls import URLPattern, URLResolver

from apps.accounts.urls.auth_urls import urlpatterns as auth_urls

app_name = "accounts"

urlpatterns: list[URLPattern | URLResolver] = [
    *auth_urls,
]
