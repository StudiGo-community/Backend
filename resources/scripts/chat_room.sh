docker compose exec -T django sh -c '
DJANGO_SETTINGS_MODULE=config.settings poetry run python manage.py shell -c "
from django.utils import timezone
from apps.chat.models.room import Room

rooms = [
  {\"id\": 1, \"name\": \"DELE 시험 준비방\", \"description\": \"#시험준비 #정보공유 #질의응답 #경험담\"},
  {\"id\": 2, \"name\": \"여행 & 현지 경험 소통방\", \"description\": \"#여행준비 #정보공유 #스페인소개 #경험담 #명소소개\"},
  {\"id\": 3, \"name\": \"영화 & 드라마 소통방\", \"description\": \"#영화감상 #영화추천 #드라마감상 #드라마추천\"},
  {\"id\": 4, \"name\": \"자유 잡담방\", \"description\": \"#원하는주제 #잡담방 #아무거나\"},
]

now = timezone.now()

for r in rooms:
    Room.objects.update_or_create(
        id=r[\"id\"],
        defaults={
            \"name\": r[\"name\"],
            \"description\": r[\"description\"],
            \"participant_count\": 0,
            \"last_message_at\": now,
        },
    )

print(\"OK: rooms upserted\")
"
'
