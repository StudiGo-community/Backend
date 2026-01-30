from django.urls import path

from apps.daily.views.question_history_views import (
    QuestionHistoryView,
)

urlpatterns = [
    path(
        "daily-questions/history",
        QuestionHistoryView.as_view(),
        name="daily-question-history",
    ),
]
