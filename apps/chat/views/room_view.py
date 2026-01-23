# 방 목록, 생성, 삭제

from django.shortcuts import get_object_or_404, render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.models.room import Room
from apps.chat.selectors.room_selector import get_rooms
from apps.chat.serializers.room_serializer import (
    RoomCreateSerializer,
    RoomDetailSerializer,
    RoomSerializer,
)
from apps.chat.services.room_service import create_room


class RoomListAPIView(APIView):
    @extend_schema(
        summary="채팅방 목록 조회",
        tags=["chat"]
    )
    def get(self, request: Request) -> Response:
        rooms = get_rooms()
        return Response(
            RoomSerializer(rooms, many=True).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="채팅방 목록 생성",
        tags=["chat"]
    )
    def post(self, request: Request) -> Response:
        serializer = RoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = create_room(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description") or None,
        )
        return Response(RoomDetailSerializer(room).data, status=status.HTTP_201_CREATED)

class RoomDetailAPIView(APIView):
    @extend_schema(
        summary="채팅방 디테일",
        tags=["chat"]
    )
    def get(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, pk=room_id)
        return Response(RoomDetailSerializer(room).data, status=status.HTTP_200_OK)
