#!/bin/bash
set -euo pipefail

python manage.py shell << 'EOF'
from django.utils import timezone
from apps.chat.models.room import Room

rooms = [
    {"id": 1, "name": "DELE 시험 준비방", "description": "#시험준비 #정보공유 #질의응답 #경험담"},
    {"id": 2, "name": "여행 & 현지 경험 소통방", "description": "#여행준비 #정보공유 #스페인소개 #경험담 #명소소개"},
    {"id": 3, "name": "영화 & 드라마 소통방", "description": "#영화감상 #영화추천 #드라마감상 #드라마추천"},
    {"id": 4, "name": "자유 잡담방", "description": "#원하는주제 #잡담방 #아무거나"},
]

now = timezone.now()

for r in rooms:
    room, created = Room.objects.update_or_create(
        id=r["id"],
        defaults={
            "name": r["name"],
            "description": r["description"],
            "participant_count": 0,
            "last_message_at": now,
        },
    )

    status = "🆕 생성" if created else "♻️ 업데이트"
    print(f"{status}: {room.id} - {room.name}")

print()
print("🎉 채팅방 초기화 완료")
EOF