# 메세지 페이징, 관리자 삭제
from __future__ import annotations

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.models.room import Room
from apps.chat.selectors.message_selector import get_room_messages
from apps.chat.serializers.message_serializer import MessageListSerializer
from apps.chat.services.message_service import assert_can_read_room_messages


class MessageListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, room_id: int) -> Response:
        room = get_object_or_404(Room, pk=room_id)

        try:
            assert_can_read_room_messages(user=request.user, room=room)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        qs = get_room_messages(room=room)

        # 쿼리스트링 페이징 (Swagger에서 테스트 쉬움)
        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", 20))

        paginator = Paginator(qs, size)
        page_obj = paginator.get_page(page)

        return Response(
            {
                "count": paginator.count,
                "page": page,
                "size": size,
                "results": MessageListSerializer(page_obj.object_list, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
