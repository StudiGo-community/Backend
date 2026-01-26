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
from apps.community.models.comments import Comment
from apps.community.serializers.report_serializers import (
    ReportCreateSerializer,
    CommentReportResponseSerializer,
)
from apps.community.services.report_services import create_comment_report


class CommentReportCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="comment_reports_create",
        summary="댓글 신고",
        description="로그인한 사용자가 부적절한 댓글을 신고한다.",
        parameters=[
            OpenApiParameter(
                name="comment_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="댓글 ID",
            )
        ],
        request=ReportCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="신고 생성 성공",
                response=CommentReportResponseSerializer,
                examples=[
                    OpenApiExample(
                        name="성공",
                        value={
                            "report_id": 6001,
                            "comment_id": 202,
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
                description="댓글 없음",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="댓글 없음",
                        value={"detail": "댓글을 찾을 수 없습니다."},
                    )
                ],
            ),
            409: OpenApiResponse(
                description="잘못된 요청",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="중복 신고",
                        value={"detail": "이미 해당 댓글을 신고했습니다."},
                    ),
                ],
            ),
        },
    )
    def post(self, request: Request, comment_id: int) -> Response:
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 댓글 존재 확인
        comment = get_object_or_404(Comment, pk=comment_id)

        # 로그인 사용자
        user = cast(User, request.user)

        # 댓글 신고 생성
        report = create_comment_report(
            comment=comment,
            reporter=user,
            reason=serializer.validated_data["reason"],
        )

        return Response(
            CommentReportResponseSerializer.from_instance(report),
            status=status.HTTP_201_CREATED,
        )