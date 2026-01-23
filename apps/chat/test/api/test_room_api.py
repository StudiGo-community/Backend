from rest_framework.test import APITestCase

from apps.chat.models.room import Room


class RoomAPITest(APITestCase):
    def test_room_list(self) -> None:
        Room.objects.create(name="test")
        Room.objects.create(name="test2")

        res = self.client.get("/api/chat/rooms/")
        assert res.status_code == 200
        assert isinstance(res.data, list)
        assert len(res.data) == 2

    def test_room_create(self) -> None:
        payload = {"name": "test"}
        res = self.client.post("/api/chat/rooms/", payload)
        assert res.status_code == 201
        assert res.data["name"] == "testRoom"

    def test_room_detail(self) -> None:
        room = Room.objects.create(name="detail")
        res = self.client.get(f"/api/chat/rooms/{room.id}/")
        assert res.status_code == 200
        assert res.data["id"] == room.id
