from datetime import date
from typing import Optional

from django.contrib.auth.models import AbstractBaseUser
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.daily.serializers.question_history_serializers import (
    QuestionHistoryResponseSerializer,
)
from apps.daily.services.question_history_services import (
    QuestionHistoryService,
)


class QuestionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["데일리"],
        summary="오늘의 문제 참여 기록 조회",
        description="로그인 사용자의 최근 문제 제출 여부를 조회합니다.",
        responses={200: QuestionHistoryResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, AbstractBaseUser)

        data = QuestionHistoryService.get_recent_history(user=user)
        serializer = QuestionHistoryResponseSerializer(data)

        return Response(serializer.data)
