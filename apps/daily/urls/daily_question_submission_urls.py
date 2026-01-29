from django.urls import path

from apps.daily.views.daily_question_submission_views import (
    DailyQuestionSubmissionTodayView,
)

urlpatterns = [
    path(
        "daily-questions/today/submission",
        DailyQuestionSubmissionTodayView.as_view(),
        name="daily-question-today-submission",
    ),
]