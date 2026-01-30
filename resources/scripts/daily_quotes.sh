#!/bin/bash

python manage.py shell << 'EOF'
from datetime import date
import calendar

from apps.daily.models.daily_quotes import DailyQuote

TODAY = date.today()
YEAR = TODAY.year

QUOTES = [
    "꾸준함이 재능을 이긴다.",
    "오늘의 선택이 내일의 나를 만든다.",
    "작은 진전도 진전이다.",
    "포기하지 않는 한 실패는 없다.",
    "느려도 멈추지 말자.",
    "완벽보다 완료가 중요하다.",
    "어제보다 나은 오늘이면 충분하다.",
    "노력은 절대 배신하지 않는다.",
    "할 수 있다고 믿는 순간 이미 반은 성공이다.",
    "성장은 불편함에서 시작된다.",
]

created_count = 0
skipped_count = 0
day_index = 0  # 연도 전체 기준 인덱스

for month in range(1, 13):
    last_day = calendar.monthrange(YEAR, month)[1]

    for day in range(1, last_day + 1):
        quote_date = date(YEAR, month, day)

        if DailyQuote.objects.filter(quote_date=quote_date).exists():
            skipped_count += 1
            day_index += 1
            continue

        content = QUOTES[day_index % len(QUOTES)]

        DailyQuote.objects.create(
            quote_date=quote_date,
            content=content,
            is_active=True,
        )
        created_count += 1
        day_index += 1

print(f"📅 대상 연도: {YEAR}년")
print(f"✅ 생성: {created_count}개")
print(f"⏭️  건너뜀: {skipped_count}개")
EOF