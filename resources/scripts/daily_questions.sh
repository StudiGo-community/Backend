#!/bin/bash

python manage.py shell << 'EOF'
from datetime import date
import calendar
import itertools

from apps.daily.models.daily_questions import DailyQuestion
from apps.daily.models.questions import Question

TODAY = date.today()
YEAR = TODAY.year
MONTH = TODAY.month

last_day = calendar.monthrange(YEAR, MONTH)[1]

# 활성화된 문제들만 가져오기
questions = list(
    Question.objects.filter(is_active=True).order_by("id")
)

if not questions:
    print("❌ 활성화된 문제가 없습니다.")
    exit(1)

question_cycle = itertools.cycle(questions)

created_count = 0
skipped_count = 0

for day in range(1, last_day + 1):
    question_date = date(YEAR, MONTH, day)

    if DailyQuestion.objects.filter(question_date=question_date).exists():
        skipped_count += 1
        continue

    question = next(question_cycle)

    DailyQuestion.objects.create(
        question=question,
        question_date=question_date,
        is_active=True,
    )
    created_count += 1

print(f"✅ 생성: {created_count}개")
print(f"⏭️  건너뜀: {skipped_count}개")
EOF