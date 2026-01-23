# 방 목록/상세 조회(정렬/최적화)

from django.db.models import QuerySet

from apps.chat.models.room import Room


def get_rooms() -> QuerySet[Room]:
    return Room.objects.all().order_by("updated_at", "created_at")

    # update가 null 이면 뒤로, 그다음 최신순
