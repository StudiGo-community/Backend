from django.urls import path

from apps.daily.views.daily_questions_views import DailyQuestionTodayView

urlpatterns = [
    path(
        "daily-questions",
        DailyQuestionTodayView.as_view(),
        name="daily-question-today",
    ),
]
