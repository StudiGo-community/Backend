from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.daily.services.daily_quotes_services import DailyQuoteService
from apps.daily.serializers.daily_quotes_serializers import DailyQuoteResponseSerializer


class DailyQuoteView(APIView):

    @extend_schema(
        tags=["데일리"],
        summary="오늘의 문장 조회",
        description="로그인한 사용자가 오늘의 문장을 조회합니다.",
        responses={
            200: DailyQuoteResponseSerializer,
        },
    )
    def get(self, request):
        data = DailyQuoteService.get_today_daily_quote()
        return Response(data, status=status.HTTP_200_OK)