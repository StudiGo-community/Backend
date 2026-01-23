from django.test import TestCase as Tast

from apps.chat.services.room_service import create_room


class TestRoomService(Tast):
    def test_create_room(self) -> None:
        room = create_room(name="test", description="test")
        assert room.id is not None
        assert room.name == "testRoom"
        assert room.participant_count == 0
        assert room.last_message_at is None
