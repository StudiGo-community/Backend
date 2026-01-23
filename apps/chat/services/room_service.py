# 방 생성/캐시 갱신(last_message_at 등)

from apps.chat.models.room import Room


def create_room(*, name: str, description: str | None = None) -> Room:
    room = Room.objects.create(
        name=name,
        description=description,
        participant_count=0,
        last_message_at=None,
    )
    return room
