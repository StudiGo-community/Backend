from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.daily.serializers.daily_quotes_serializers import DailyQuoteResponseSerializer
from apps.daily.services.daily_quotes_services import DailyQuoteService


class DailyQuoteView(APIView):

    @extend_schema(
        tags=["데일리"],
        summary="오늘의 문장 조회",
        description="로그인한 사용자가 오늘의 문장을 조회합니다.",
        responses={
            200: DailyQuoteResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        data = DailyQuoteService.get_today_daily_quote()
        return Response(data, status=status.HTTP_200_OK)
