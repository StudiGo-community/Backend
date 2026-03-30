# 관리자 차단, 해제, 목록
from __future__ import annotations

from typing import List, cast

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import serialize

from apps.accounts.models import User
from apps.chat.models.bans import Bans
from apps.chat.serializers.ban_serializer import (
    BanCreateSerializer,
    BanListResponseSerializer,
    BanSerializer,
    BanUpdateSerializer,
)
from apps.chat.services.ban_service import create_ban, update_ban


def _is_admin(user: User) -> bool:
    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or getattr(user, "role", "") == "ADMIN"
    )


def _active_filter() -> Q:
    now = timezone.now()
    return Q(is_active=True) & (Q(ends_at__isnull=True) | Q(ends_at__gt=now))


class AdminBanListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="사용자 채팅 차단/해제 조회",
        tags=["채팅(관리자)"],
        parameters=[
            OpenApiParameter(name="active", required=False, type=bool),
            OpenApiParameter(name="expired", required=False, type=bool),
            OpenApiParameter(name="user_id", required=False, type=int),
            OpenApiParameter(name="room_id", required=False, type=int),
            OpenApiParameter(name="order_by", required=False, type=str),
            OpenApiParameter(name="sort", required=False, type=str),
            OpenApiParameter(name="page", required=False, type=int),
            OpenApiParameter(name="size", required=False, type=int),
        ],
        responses=BanListResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        admin = cast(User, request.user)
        if not _is_admin(admin):
            return Response(
                {"detail": "관리자 권한이 필요합니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        qs = Bans.objects.all()

        # filters
        active = request.query_params.get("active")
        expired = request.query_params.get("expired")
        user_id = request.query_params.get("user_id")
        room_id = request.query_params.get("room_id")

        if user_id:
            qs = qs.filter(user_id=int(user_id))
        if room_id:
            qs = qs.filter(room_id=int(room_id))

        if active == "true":
            qs = qs.filter(_active_filter())

        if expired == "true":
            qs = qs.filter(
                is_active=True, ends_at__isnull=False, ends_at__lte=timezone.now()
            )

        order_by = request.query_params.get("order_by") or "created_at"
        sort = request.query_params.get("sort") or "desc"
        if order_by not in ("created_at", "updated_at"):
            order_by = "created_at"
        prefix = "" if sort == "asc" else "-"
        qs = qs.order_by(f"{prefix}{order_by}")

        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", 20))
        paginator = Paginator(qs, size)
        page_obj = paginator.get_page(page)

        items: List[Bans] = list(page_obj.object_list)
        serializer = BanSerializer(items, many=True)

        return Response(
            {
                "items": serializer.data,
                "page": page,
                "total": paginator.count,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="사용자 채팅 차단/해제 생성",
        tags=["채팅(관리자)"],
        request=BanCreateSerializer,
        responses=BanSerializer,
    )
    def post(self, request: Request) -> Response:
        admin = cast(User, request.user)
        if not _is_admin(admin):
            return Response(
                {"detail": "관리자 권한이 필요합니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        ban = create_ban(
            admin=admin,
            user_id=data["user_id"],
            room_id=data.get("room_id"),
            ends_at=data.get("ends_at"),
            reason=data.get("reason"),
        )

        return Response({"ban": BanSerializer(ban).data}, status=status.HTTP_200_OK)


class AdminBanUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="사용자 채팅 차단/해제 수정",
        tags=["채팅(관리자)"],
        request=BanUpdateSerializer,
        responses=BanSerializer,
    )
    def patch(self, request: Request, ban_id: int) -> Response:
        admin = cast(User, request.user)
        if not _is_admin(admin):
            return Response(
                {"detail": "관리자 권한이 필요합니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BanUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        v = serializer.validated_data
        ban = update_ban(
            ban_id=ban_id,
            is_active=v.get("is_active"),
            ends_at=(
                v.get("ends_at") if "ends_at" in v else None
            ),  # 키 있을 때만 반영하고 싶으면 서비스 조정
            reason=v.get("reason"),
        )

        return Response({"ban": BanSerializer(ban).data}, status=status.HTTP_200_OK)
