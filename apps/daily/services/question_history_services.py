from datetime import date, timedelta
from typing import Any, Dict, List, Optional, cast

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet
from django.utils import timezone

from apps.daily.models.daily_question_submissions import DailyQuestionSubmission
from apps.daily.models.daily_questions import DailyQuestion


class QuestionHistoryService:
    DAYS = 4  # 유지보수용 오늘 포함 4일차까지 가져오기

    @classmethod
    def get_recent_history(
        cls,
        *,
        user: AbstractBaseUser,
    ) -> Dict[str, List[Dict[str, Any]]]:
        today = timezone.localdate()
        start_date = today - timedelta(days=cls.DAYS - 1)

        submissions = DailyQuestionSubmission.objects.filter(  # type: ignore[attr-defined]
            user=user,
            daily_question__question_date__range=(start_date, today),
        ).select_related(
            "daily_question"
        )

        submitted_dates = {
            submission.daily_question.question_date for submission in submissions
        }

        results: List[Dict[str, Any]] = []

        for i in range(cls.DAYS):
            target_date = today - timedelta(days=i)
            results.append(
                {
                    "date": target_date,
                    "is_submitted": target_date in submitted_dates,
                }
            )

        return {"results": results}
