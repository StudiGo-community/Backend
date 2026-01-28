# apps/chat/views/message_view.py
from __future__ import annotations

from typing import cast

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.chat.models.room import Room
from apps.chat.selectors.message_selector import get_room_messages
from apps.chat.serializers.message_serializer import (
    MessageListSerializer,
    MessageCreateSerializer,
    MessageDetailSerializer,
)
from apps.chat.services.message_service import (
    assert_can_read_room_messages,
    send_message,
)


class MessageListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="채팅방 메세지 조회",
        tags=["채팅"],
        parameters=[
            OpenApiParameter(name="page", required=False, type=int, description="페이지 번호"),
            OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
        ],
    )
    def get(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, pk=room_id)
        user = cast(User, request.user)

        try:
            assert_can_read_room_messages(user=user, room=room)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        cursor = request.query_params.get("cursor")
        cursor_id = int(cursor) if cursor else None
        size = int(request.query_params.get("size", 20))

        qs = get_room_messages(room=room, cursor=cursor_id, size=size)
        items = list(qs)

        next_cursor = items[-1].id if items else None
        has_more = len(items) == size

        return Response(
            {
                "room_id": room.id,
            "messages": MessageListSerializer(items, many=True).data,
            "next_cursor": next_cursor,
            "has_more": has_more,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="채팅방 메세지 전송",
        tags=["채팅"],
        request=MessageCreateSerializer,
        responses=MessageListSerializer,
    )
    def post(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, pk=room_id)
        user = cast(User, request.user)

        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            assert_can_read_room_messages(user=user, room=room)
            msg = send_message(
                user=user,
                room=room,
                content=serializer.validated_data["content"],
            )
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            MessageListSerializer(msg).data,
            status=status.HTTP_201_CREATED,
        )
