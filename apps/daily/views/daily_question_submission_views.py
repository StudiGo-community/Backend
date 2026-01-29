from typing import List, Type

from django.contrib.auth.models import AbstractBaseUser
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.daily.serializers.daily_question_submission_serializers import (
    DailyQuestionSubmissionCreateSerializer,
    DailyQuestionSubmissionResponseSerializer,
)
from apps.daily.services.daily_question_submission_services import (
    AlreadySubmittedError,
    TodayQuestionNotFoundError,
    submit_today_question,
)


class DailyQuestionSubmissionTodayView(APIView):
    """
    오늘의 문제 제출 API
    """

    permission_classes: List[Type[BasePermission]] = [IsAuthenticated]

    @extend_schema(
        tags=["데일리"],
        summary="오늘의 문제 제출",
        description=(
            "로그인 사용자가 오늘의 문제를 1회 제출합니다.\n\n"
            "- 하루 1문제, 사용자당 1회만 제출 가능\n"
            "- 제출 즉시 정답 여부가 판별됩니다.\n"
            "- 제출 성공 시 자동 출석체크가 처리됩니다."
        ),
        request=DailyQuestionSubmissionCreateSerializer,
        responses={
            201: DailyQuestionSubmissionResponseSerializer,
            401: OpenApiResponse(
                description="인증이 필요합니다.",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                    },
                },
            ),
            404: OpenApiResponse(
                description="오늘의 문제가 존재하지 않습니다.",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                    },
                },
            ),
            409: OpenApiResponse(
                description="이미 오늘의 문제를 제출했습니다.",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                    },
                },
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = DailyQuestionSubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = request.user
            if not isinstance(user, AbstractBaseUser):
                raise PermissionDenied("로그인이 필요합니다.")

            result = submit_today_question(
                user=user,
                submitted_answer_text=serializer.validated_data[
                    "submitted_answer_text"
                ],
            )
        except AlreadySubmittedError as e:
            return Response(
                {"detail": str(e.detail)},
                status=status.HTTP_409_CONFLICT,
            )
        except TodayQuestionNotFoundError as e:
            return Response(
                {"detail": str(e.detail)},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = DailyQuestionSubmissionResponseSerializer(
            result.submission
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
