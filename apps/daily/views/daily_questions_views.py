from typing import List, Type

from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.daily.serializers.daily_questions_serializers import (
    DailyQuestionTodayResponseSerializer,
)
from apps.daily.services.daily_questions_services import DailyQuestionService


class DailyQuestionTodayView(APIView):
    authentication_classes: List[Type[BaseAuthentication]] = []
    permission_classes: List[Type[BasePermission]] = []

    @extend_schema(
        tags=["데일리"],
        summary="오늘의 문제 조회",
        description="오늘의 문제를 조회합니다. (비로그인 가능)",
        responses={
            200: DailyQuestionTodayResponseSerializer,
            404: OpenApiResponse(
                description="오늘의 문제가 등록되지 않았습니다.",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                    },
                },
            ),
        },
    )
    def get(self, request: Request) -> Response:
        try:
            data = DailyQuestionService.get_today_daily_question()
        except Http404:
            return Response(
                {"detail": "오늘의 문제가 등록되지 않았습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(data, status=status.HTTP_200_OK)
