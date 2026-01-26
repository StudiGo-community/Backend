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
from apps.community.models.posts import Post
from apps.community.serializers.comment_serializers import (
    CommentCreateSerializer,
    CommentListItemSerializer,
    CommentListResponseSerializer,
    CommentResponseSerializer,
)
from apps.community.services.comment_services import (
    create_comment,
    delete_comment,
    get_post_comments,
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

        user = cast(User, request.user)

        comment = create_comment(
            post_id=post_id,
            author=user,
            content=serializer.validated_data["content"],
        )

        return Response(
            CommentResponseSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class CommentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="comments_delete",
        summary="댓글 삭제",
        description="댓글 작성자가 댓글을 삭제합니다.",
        parameters=[
            OpenApiParameter(
                name="comment_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="댓글 ID",
            )
        ],
        responses={
            204: OpenApiResponse(description="삭제 완료"),
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
            403: OpenApiResponse(
                description="삭제 권한 없음",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="권한 없음",
                        value={"detail": "삭제 권한이 없습니다."},
                    )
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
        },
    )
    def delete(self, request: Request, post_id: int, comment_id: int) -> Response:
        comment = get_object_or_404(
            Comment,
            pk=comment_id,
            status=PostCommentStatus.ACTIVE,
        )
        user = cast(User, request.user)

        if comment.author != request.user:
            return Response(
                {"detail": "삭제 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        delete_comment(comment_id=comment_id, user=user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListAPIView(APIView):
    @extend_schema(
        tags=["커뮤니티"],
        operation_id="comments_list",
        summary="댓글 조회",
        description="특정 게시글에 달린 댓글을 페이지네이션 방식으로 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                required=False,
                description="페이지 번호 (기본 1)",
            ),
            OpenApiParameter(
                name="size",
                type=OpenApiTypes.INT,
                required=False,
                description="페이지당 댓글 수 (기본 10)",
            ),
            OpenApiParameter(
                name="sort",
                enum=["LATEST", "OLDEST"],
                required=False,
                description="정렬 방식 (기본 LATEST)",
            ),
        ],
        responses={200: CommentListResponseSerializer},
    )
    def get(self, request: Request, post_id: int) -> Response:
        post = get_object_or_404(Post, pk=post_id)

        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", 10))
        sort = request.query_params.get("sort", "LATEST")

        result = get_post_comments(
            post=post,
            page=page,
            size=size,
            sort=sort,  # type: ignore[arg-type]
        )

        return Response(
            {
                "comments": CommentListItemSerializer(
                    result["comments"], many=True
                ).data,
                "pagination": {
                    "page": result["page"],
                    "size": result["size"],
                    "total_count": result["total_count"],
                    "total_pages": result["total_pages"],
                    "has_next": result["has_next"],
                },
            },
            status=status.HTTP_200_OK,
        )
