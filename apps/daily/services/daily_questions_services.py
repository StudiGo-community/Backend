from datetime import date, datetime, time, timedelta
from typing import Any, Dict, cast

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware

from apps.daily.models.daily_questions import DailyQuestion


class DailyQuestionService:
    CACHE_TTL = 60 * 60 * 24  # 24시간

    @classmethod
    def get_today_daily_question(cls) -> Dict[str, Any]:
        today = date.today()
        cache_key = f"daily_question:{today}"

        cached = cache.get(cache_key)
        if cached is not None:
            return cast(Dict[str, Any], cached)

        daily_question = get_object_or_404(
            DailyQuestion.objects.select_related("question"),  # type: ignore[attr-defined]
            question_date=today,
            is_active=True,
            question__is_active=True,
        )

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
