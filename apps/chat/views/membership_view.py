# 입장, 퇴장
from __future__ import annotations

from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.models import Room
from apps.chat.serializers.membership_serializer import RoomJoinResponseSerializer
from apps.chat.services.membership_service import join_room, exit_room


class ChatRoomJoinAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="채팅방 입장", tags=["채팅"])
    def post(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, pk=room_id)

        try:
            join_room(user=request.user, room=room)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                "message": "채팅방에 입장했습니다.",
                "room": {"id": room.id, "name": room.name},
            },
            status=status.HTTP_200_OK,
        )

class ChatRoomExitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="채팅방 퇴장", tags=["채팅"])
    def post(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, pk=room_id)

        try:
            exit_room(user=request.user, room=room)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "채팅방에서 퇴장했습니다."},
            status=status.HTTP_200_OK,
        )
