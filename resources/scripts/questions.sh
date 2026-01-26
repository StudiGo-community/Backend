#!/bin/bash

python manage.py shell << 'EOF'
from apps.daily.models.questions import Question

# 이번 달 문제 예시 데이터
QUESTIONS = [
    {
        "title": "SQL 기본",
        "description": "다음 질문에 답하세요.",
        "prompt": "SELECT 문에서 조건을 거는 키워드는 ______ 이다.",
        "answer_text": "WHERE",
        "explanation": "SELECT 문에서 조건을 지정할 때 WHERE 절을 사용한다.",
    },
    {
        "title": "Python 기본",
        "description": "다음 질문에 답하세요.",
        "prompt": "리스트의 길이를 구하는 함수는 ______ 이다.",
        "answer_text": "len",
        "explanation": "len() 함수는 시퀀스의 길이를 반환한다.",
    },
    {
        "title": "Django ORM",
        "description": "다음 질문에 답하세요.",
        "prompt": "모델 조회 시 하나의 객체를 반환하는 메서드는 ______ 이다.",
        "answer_text": "get",
        "explanation": "get()은 단일 객체를 조회하며 없거나 여러 개면 예외가 발생한다.",
    },
    {
        "title": "HTTP 기본",
        "description": "다음 질문에 답하세요.",
        "prompt": "리소스를 생성할 때 주로 사용하는 HTTP 메서드는 ______ 이다.",
        "answer_text": "POST",
        "explanation": "POST 메서드는 서버에 리소스를 생성할 때 사용된다.",
    },
    {
        "title": "Git 기본",
        "description": "다음 질문에 답하세요.",
        "prompt": "현재 변경사항을 임시로 저장하는 명령어는 ______ 이다.",
        "answer_text": "stash",
        "explanation": "git stash는 작업 중인 변경사항을 임시로 저장한다.",
    },
]

created = 0
skipped = 0

for q in QUESTIONS:
    obj, is_created = Question.objects.get_or_create(
        title=q["title"],
        defaults={
            "description": q["description"],
            "prompt": q["prompt"],
            "answer_text": q["answer_text"],
            "explanation": q["explanation"],
            "is_active": True,
        },
    )

    if is_created:
        created += 1
    else:
        skipped += 1

print(f"✅ 생성된 문제: {created}개")
print(f"⏭️  이미 존재하여 건너뜀: {skipped}개")
EOF