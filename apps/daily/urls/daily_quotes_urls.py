from django.urls import URLPattern, URLResolver, path

from apps.daily.views.daily_quotes_views import DailyQuoteView

urlpatterns: list[URLPattern | URLResolver] = [
    path("daily-quotes", DailyQuoteView.as_view()),
]
