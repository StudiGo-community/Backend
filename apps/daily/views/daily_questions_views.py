from typing import List, Type

from django.contrib.auth.models import AbstractBaseUser
from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.daily.serializers.daily_questions_serializers import (
    DailyQuestionSolvedResponseSerializer,
    DailyQuestionUnsolvedResponseSerializer,
)
from apps.daily.services.daily_questions_services import DailyQuestionService


class DailyQuestionTodayView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["데일리"],
        summary="오늘의 문제 조회",
        description=(
            "오늘의 문제를 조회합니다.\n\n"
            "- 아직 풀지 않은 경우: 문제 정보 반환\n"
            "- 이미 푼 경우: 정답 결과 반환\n"
            "(비로그인 사용자도 조회 가능)"
        ),
        responses={
            200: OpenApiResponse(
                response=DailyQuestionUnsolvedResponseSerializer,
                description="오늘의 문제 (미풀이 시)",
            ),
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
            user = request.user if isinstance(request.user, AbstractBaseUser) else None
            data = DailyQuestionService.get_today_daily_question(user=user)
        except Http404:
            return Response(
                {"detail": "오늘의 문제가 등록되지 않았습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "daily_question_id" in data:
            return Response(
                DailyQuestionUnsolvedResponseSerializer(data).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            DailyQuestionSolvedResponseSerializer(data).data,
            status=status.HTTP_200_OK,
        )
