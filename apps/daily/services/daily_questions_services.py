from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Optional, cast

from django.contrib.auth.models import AbstractBaseUser
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware

from apps.daily.models.daily_question_submissions import DailyQuestionSubmission
from apps.daily.models.daily_questions import DailyQuestion


class DailyQuestionService:
    CACHE_TTL = 60 * 60 * 24  # 24시간

    @classmethod
    def get_today_daily_question(
        cls,
        *,
        user: Optional[AbstractBaseUser],
    ) -> Dict[str, Any]:
        today = date.today()
        cache_key = f"daily_question:{today}"

        daily_question = get_object_or_404(
            cast(Any, DailyQuestion).objects.select_related("question"),
            question_date=today,
            is_active=True,
            question__is_active=True,
        )

        if user is not None and user.is_authenticated:
            submission = (
                cast(Any, DailyQuestionSubmission)
                .objects.filter(
                    daily_question=daily_question,
                    user=user,
                )
                .select_related("daily_question__question")
                .first()
            )

            if submission is not None:
                return {
                    "date": daily_question.question_date,
                    "explanation": (
                        submission.daily_question.question.explanation or ""
                    ),
                    "answer_correct": (
                        submission.daily_question.question.answer_text or ""
                    ),
                    "answer_user": submission.submitted_answer_text or "",
                    "is_correct": submission.is_correct,
                }

        cached: Optional[Dict[str, Any]] = cache.get(cache_key)
        if cached is not None:
            return cached

        expires_at = make_aware(datetime.combine(today + timedelta(days=1), time.min))

        data: Dict[str, Any] = {
            "question_date": daily_question.question_date,
            "daily_question_id": daily_question.id,
            "question": {
                "id": daily_question.question.id,
                "title": daily_question.question.title,
                "description": daily_question.question.description,
                "prompt": daily_question.question.prompt,
            },
            "expires_at": expires_at,
        }

        cache.set(cache_key, data, cls.CACHE_TTL)
        return data
