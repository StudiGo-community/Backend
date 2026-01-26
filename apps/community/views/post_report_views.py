from typing import cast

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.community.models.posts import Post
from apps.community.serializers.report_serializers import (
    ReportCreateSerializer,
    PostReportResponseSerializer,
)
from apps.community.services.report_services import create_post_report


class PostReportCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="post_reports_create",
        summary="게시글 신고",
        description="로그인한 사용자가 부적절한 게시글을 신고한다.",
        parameters=[
            OpenApiParameter(
                name="post_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="게시글 ID",
            )
        ],
        request=ReportCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="신고 생성 성공",
                response=PostReportResponseSerializer,
                examples=[
                    OpenApiExample(
                        name="성공",
                        value={
                            "report_id": 5001,
                            "post_id": 101,
                            "reason": "욕설/비방",
                            "status": "RECEIVED",
                            "created_at": "2026-01-13T15:12:00+09:00",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="잘못된 요청",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="reason 누락/공백",
                        value={"reason": ["신고 사유는 필수입니다."]},
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="인증 필요",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(name="인증 필요", value={"detail": "인증이 필요합니다."})
                ],
            ),
            404: OpenApiResponse(
                description="게시글 없음",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="게시글 없음",
                        value={"detail": "게시글을 찾을 수 없습니다."},
                    )
                ],
            ),
            409: OpenApiResponse(
                description="잘못된 요청",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="중복 신고",
                        value={"detail": "이미 해당 게시글을 신고했습니다."},
                    ),
                ],
            ),
        },
    )
    def post(self, request: Request, post_id: int) -> Response:
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 게시글 존재 확인
        post = get_object_or_404(Post, pk=post_id)

        # 로그인 사용자
        user = cast(User, request.user)

        # 게시글 신고 생성
        report = create_post_report(
            post=post,
            reporter=user,
            reason=serializer.validated_data["reason"],
        )

        return Response(
            PostReportResponseSerializer.from_instance(report),
            status=status.HTTP_201_CREATED,
        )