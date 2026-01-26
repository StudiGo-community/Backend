from datetime import date
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from apps.daily.models.daily_quotes import DailyQuote
from apps.core.translation import translate_ko_to_es

class DailyQuoteService:
    CACHE_TTL = 60 * 60 * 24  # 24시간

    @classmethod
    def get_today_daily_quote(cls):
        today = date.today()
        cache_key = f"daily_quote:{today}"

        cached = cache.get(cache_key)
        if cached:
            return cached

        daily_quote = get_object_or_404(
            DailyQuote,
            quote_date=today,
            is_active=True,
        )

        data = {
            "date": today,
            "quotes": {
                "ko": daily_quote.content,
                "es": translate_ko_to_es(daily_quote.content),
            },
            "refreshed_at": daily_quote.created_at,
        }

        cache.set(cache_key, data, cls.CACHE_TTL)
        return data