from django.urls import URLPattern, URLResolver

from apps.daily.urls.daily_quotes_urls import urlpatterns as daily_quotes_urls

app_name = "daily"

urlpatterns: list[URLPattern | URLResolver] = [
    *daily_quotes_urls,
]
