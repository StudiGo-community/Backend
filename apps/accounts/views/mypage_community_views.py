from typing import Any, cast

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers.mypage_community_serializers import (
    BulkDeleteSerializer,
    MyCommentListItemSerializer,
    MyLikedPostListItemSerializer,
    MyPostListItemSerializer,
)
from apps.accounts.services.mypage.community_service import (
    MyPageCommunityService,
    SortLatestOldest,
)


class PermissionClass(APIView):
    permission_classes = (IsAuthenticated,)


def _parse_int(value: Any, default: int = 10, *, max_value: int | None = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if parsed <= 0:
        return default
    if max_value is not None:
        return min(parsed, max_value)
    return parsed


def _parse_sort(value: Any) -> SortLatestOldest:
    return "oldest" if str(value).lower() == "oldest" else "latest"


def _bulk_delete_ids(request: Request) -> list[int]:
    serializer = BulkDeleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return cast(list[int], serializer.validated_data["ids"])


class MyPostsAPIView(PermissionClass):
    """마이페이지 > 내 게시글"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = MyPageCommunityService()

    @extend_schema(
        tags=["마이페이지"],
        operation_id="mypage_my_posts_list",
        summary="내 게시글 조회",
        description="마이페이지에서 로그인 사용자가 작성한 게시글 목록을 조회합니다.\n\n"
        "- 기본 정렬: 최신순(latest)\n"
        "- 정렬 옵션: latest / oldest\n"
        "- 페이지네이션: page, size\n"
        "- 게시글이 없으면 message를 반환합니다.",
        parameters=[
            OpenApiParameter(
                name="page",
                required=False,
                type=OpenApiTypes.INT,
                description="페이지(기본 1)",
            ),
            OpenApiParameter(
                name="size",
                required=False,
                type=OpenApiTypes.INT,
                description="페이지당 개수(기본 10)",
            ),
            OpenApiParameter(
                name="sort",
                required=False,
                type=OpenApiTypes.STR,
                description="정렬(latest|oldest, 기본 latest)",
            ),
        ],
        responses={
            200: OpenApiResponse(),
        },
        examples=[
            OpenApiExample(
                name="게시글 없음",
                summary="",
                value={
                    "posts": [],
                    "pagination": {
                        "current_page": 1,
                        "total_pages": 0,
                        "total_count": 0,
                        "has_next": False,
                        "has_previous": False,
                    },
                    "message": "작성한 게시글이 없습니다.",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request: Request) -> Response:
        user = self.service.get_authenticated_user(request)

        page = _parse_int(request.query_params.get("page"), 1)
        size = _parse_int(request.query_params.get("size"), 10)
        sort = _parse_sort(request.query_params.get("sort"))

        result = self.service.get_my_posts(user=user, page=page, size=size, sort=sort)

        posts = MyPostListItemSerializer(result["items"], many=True).data
        payload: dict[str, Any] = {"posts": posts, "pagination": result["pagination"]}
        if result["pagination"]["total_count"] == 0:
            payload["message"] = "작성한 게시글이 없습니다."

        return Response(payload, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["마이페이지"],
        operation_id="mypage_my_posts_bulk_delete",
        summary="내 게시글 삭제(체크박스)",
        description="체크박스로 선택한 내 게시글을 일괄 삭제(soft delete)합니다.",
        request=BulkDeleteSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def delete(self, request: Request) -> Response:
        user = self.service.get_authenticated_user(request)
        ids = _bulk_delete_ids(request)
        result = self.service.delete_my_posts(user=user, post_ids=ids)

        return Response(
            {"deleted_count": result.deleted_count}, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["마이페이지"],
        operation_id="mypage_my_posts_bulk_delete_post",
        summary="내 게시글 삭제(체크박스, POST)",
        description=(
            "체크박스로 선택한 내 게시글을 일괄 삭제(soft delete)합니다.\n"
            "DELETE body를 처리하지 못하는 일부 클라이언트/프록시 환경을 위해 POST도 지원합니다."
        ),
        request=BulkDeleteSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def post(self, request: Request) -> Response:
        user = self.service.get_authenticated_user(request)
        ids = _bulk_delete_ids(request)
        result = self.service.delete_my_posts(user=user, post_ids=ids)

        return Response(
            {"deleted_count": result.deleted_count}, status=status.HTTP_200_OK
        )


class MyCommentsAPIView(PermissionClass):
    """마이페이지 > 내 댓글"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = MyPageCommunityService()

    @extend_schema(
        tags=["마이페이지"],
        operation_id="mypage_my_comments_list",
        summary="내 댓글 조회",
        description=(
            "마이페이지에서 로그인 사용자가 작성한 댓글 목록을 조회합니다.\n\n"
            "- 기본 정렬: 최신순(latest)\n"
            "- 원본 게시글이 삭제된 경우 is_deleted=true\n"
            "- 페이지네이션: page, size"
        ),
        parameters=[
            OpenApiParameter(
                name="page",
                required=False,
                type=OpenApiTypes.INT,
                description="페이지(기본 1)",
            ),
            OpenApiParameter(
                name="size",
                required=False,
                type=OpenApiTypes.INT,
                description="페이지당 개수(기본 10)",
            ),
            OpenApiParameter(
                name="sort",
                required=False,
                type=OpenApiTypes.STR,
                description="정렬(latest|oldest, 기본 latest)",
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request: Request) -> Response:
        user = self.service.get_authenticated_user(request)

        page = _parse_int(request.query_params.get("page"), 1)
        size = _parse_int(request.query_params.get("size"), 10)
        sort = _parse_sort(request.query_params.get("sort"))

        result = self.service.get_my_comments(
            user=user, page=page, size=size, sort=sort
        )

        comments = MyCommentListItemSerializer(result["items"], many=True).data
        payload: dict[str, Any] = {
            "comments": comments,
            "pagination": result["pagination"],
        }
        if result["pagination"]["total_count"] == 0:
            payload["message"] = "작성한 댓글이 없습니다."

        return Response(payload, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["마이페이지"],
        operation_id="mypage_my_comments_bulk_delete",
        summary="내 댓글 삭제(체크박스)",
        description="체크박스로 선택한 내 댓글을 일괄 삭제(soft delete)합니다.",
        request=BulkDeleteSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def delete(self, request: Request) -> Response:
        user = self.service.get_authenticated_user(request)
        ids = _bulk_delete_ids(request)
        result = self.service.delete_my_comments(user=user, comment_ids=ids)

        return Response(
            {"deleted_count": result.deleted_count}, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["마이페이지"],
        operation_id="mypage_my_comments_bulk_delete_post",
        summary="내 댓글 삭제(체크박스, POST)",
        description=(
            "체크박스로 선택한 내 댓글을 일괄 삭제(soft delete)합니다.\n"
            "DELETE body를 처리하지 못하는 일부 클라이언트/프록시 환경을 위해 POST도 지원합니다."
        ),
        request=BulkDeleteSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def post(self, request: Request) -> Response:
        user = self.service.get_authenticated_user(request)
        ids = _bulk_delete_ids(request)
        result = self.service.delete_my_comments(user=user, comment_ids=ids)

        return Response(
            {"deleted_count": result.deleted_count}, status=status.HTTP_200_OK
        )


class MyLikedPostsAPIView(PermissionClass):
    """마이페이지 > 좋아요한 게시글"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = MyPageCommunityService()

    @extend_schema(
        tags=["마이페이지"],
        operation_id="mypage_my_liked_posts_list",
        summary="좋아요한 게시글 조회",
        description=(
            "로그인 사용자가 좋아요한 게시글 목록을 조회합니다.\n\n"
            "- 기본 정렬: 좋아요한 최신순\n"
            "- 삭제된 게시글이면 is_deleted=true + title='삭제된 게시글입니다.'\n"
            "- 페이지네이션: page, size"
        ),
        parameters=[
            OpenApiParameter(
                name="page",
                required=False,
                type=OpenApiTypes.INT,
                description="페이지(기본 1)",
            ),
            OpenApiParameter(
                name="size",
                required=False,
                type=OpenApiTypes.INT,
                description="페이지당 개수(기본 10)",
            ),
            OpenApiParameter(
                name="sort",
                required=False,
                type=OpenApiTypes.STR,
                description="정렬(latest|oldest, 기본 latest)",
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request: Request) -> Response:
        user = self.service.get_authenticated_user(request)

        page = _parse_int(request.query_params.get("page"), 1)
        size = _parse_int(request.query_params.get("size"), 10)
        sort = _parse_sort(request.query_params.get("sort"))

        result = self.service.get_my_liked_posts(
            user=user, page=page, size=size, sort=sort
        )

        liked_posts = MyLikedPostListItemSerializer(result["items"], many=True).data
        payload: dict[str, Any] = {
            "liked_posts": liked_posts,
            "pagination": result["pagination"],
        }
        if result["pagination"]["total_count"] == 0:
            payload["message"] = "좋아한 게시글이 없습니다."

        return Response(payload, status=status.HTTP_200_OK)
