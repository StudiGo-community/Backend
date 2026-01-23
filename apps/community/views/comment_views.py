from typing import Any

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

from apps.community.models.comments import Comment
from apps.community.models.posts import Post
from apps.community.serializers.comment_serializers import (
    CommentCreateSerializer,
    CommentResponseSerializer,
)
from apps.community.services.comment_services import (
    create_comment,
    delete_comment,
)
from apps.core.enumeration.community_enumerations import PostCommentStatus


class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="comments_create",
        summary="댓글 작성",
        description="로그인 사용자가 특정 게시글에 댓글을 작성합니다.",
        parameters=[
            OpenApiParameter(
                name="post_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="게시글 ID",
            )
        ],
        request=CommentCreateSerializer,
        responses={
            201: CommentResponseSerializer,
            400: OpenApiResponse(
                description="잘못된 요청",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="content 누락",
                        value={"detail": "content는 필수입니다."},
                    )
                ],
            ),
            401: OpenApiResponse(
                description="인증 필요",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="인증 필요",
                        value={"detail": "인증이 필요합니다."},
                    )
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
        },
    )
    def post(self, request: Request, post_id: int) -> Response:
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 게시글 존재 확인
        post = get_object_or_404(Post, pk=post_id)

        comment = create_comment(
            post_id=post.id,
            author=request.user,
            content=serializer.validated_data["content"],
        )

        return Response(
            CommentResponseSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )
