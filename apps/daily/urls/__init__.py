from django.urls import URLPattern, URLResolver

from apps.daily.urls.daily_questions_urls import urlpatterns as daily_questions_urls
from apps.daily.urls.daily_quotes_urls import urlpatterns as daily_quotes_urls
from apps.daily.urls.daily_question_submission_urls import urlpatterns as daily_question_submission_urls

app_name = "daily"

urlpatterns: list[URLPattern | URLResolver] = [
    *daily_quotes_urls,
    *daily_questions_urls,
    *daily_question_submission_urls,
]
