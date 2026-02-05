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

from apps.community.models.posts import Post
from apps.community.serializers.post_serializers import (
    PostCreateResponseSerializer,
    PostCreateSerializer,
    PostDetailResponseSerializer,
    PostLikeResponseSerializer,
    PostListItemSerializer,
    PostPatchResponseSerializer,
    PostPatchSerializer,
)
from apps.community.services.post_services import (
    create_post,
    delete_post,
    get_post_detail,
    get_post_list,
    like_post,
    patch_post,
    unlike_post,
)
from apps.core.choices.community_choices import PostCategory
from apps.core.choices.query_choices import SearchField, Sort
from apps.core.pagination import PostsPagination


class PostCreateListAPIView(APIView):
    def get_permissions(self) -> Any:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return []

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="posts_create",
        summary="게시글 등록",
        description="로그인 사용자가 게시글을 작성하고 등록합니다.",
        request=PostCreateSerializer,
        responses={201: PostCreateResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = create_post(
            author=request.user,
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            category=serializer.validated_data["category"],
            images=serializer.validated_data.get("images"),
            thumbnail_url=serializer.validated_data.get("thumbnail_url"),
        )

        return Response(
            PostCreateResponseSerializer(post).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="posts_list",
        summary="게시글 목록 조회",
        description="게시글 목록을 조회합니다. (비로그인 사용자도 가능)",
        parameters=[
            OpenApiParameter(
                name="page",
                required=False,
                type=OpenApiTypes.INT,
                description="페이지",
            ),
            OpenApiParameter(
                name="category",
                enum=[choice for choice, _ in PostCategory.choices],
                location=OpenApiParameter.QUERY,
                description="카테고리 필터(미지정 시 전체)",
            ),
            OpenApiParameter(
                name="sort",
                enum=[value for value, _ in Sort.choices],
                location=OpenApiParameter.QUERY,
                description="정렬(기본 latest)",
            ),
            OpenApiParameter(
                name="q",
                required=False,
                type=OpenApiTypes.STR,
                description="검색 키워드",
            ),
            OpenApiParameter(
                name="search_field",
                enum=[value for value, _ in SearchField.choices],
                location=OpenApiParameter.QUERY,
                description="검색 범위(기본 all)",
            ),
        ],
        responses={200: PostListItemSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        category = request.query_params.get("category")
        sort = request.query_params.get("sort", "latest")
        keyword = request.query_params.get("q")
        search_field = request.query_params.get("search_field", "all")

        post_queryset = get_post_list(
            user=request.user,
            category=category,
            sort=sort,
            keyword=keyword,
            search_field=search_field,
        )

        paginator = PostsPagination()
        paginated_queryset = paginator.paginate_queryset(
            post_queryset, request, view=self
        )
        serializer = PostListItemSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class PostDetailAPIView(APIView):
    def get_permissions(self) -> Any:
        if self.request.method == "PATCH":
            return [IsAuthenticated()]
        return []

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="posts_detail",
        summary="게시글 상세 조회",
        description="특정 게시글의 상세 정보를 조회합니다. (비로그인 가능, 로그인 시 is_liked 제공)",
        responses={200: PostDetailResponseSerializer},
    )
    def get(self, request: Request, post_id: int) -> Response:
        post = get_post_detail(request=request, user=request.user, post_id=post_id)
        if post is None:
            return Response(
                {"detail": "게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            PostDetailResponseSerializer(post).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="posts_delete",
        summary="게시글 삭제",
        description="작성자 또는 ADMIN이 게시글을 삭제합니다.",
        responses={
            204: OpenApiResponse(description="삭제 완료"),
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
            404: OpenApiResponse(description="게시글 없음"),
        },
    )
    def delete(self, request: Request, post_id: int) -> Response:
        post = get_object_or_404(Post, pk=post_id)
        user = request.user

        is_admin = getattr(user, "role", None) == "ADMIN"

        if post.author != user and not is_admin:
            return Response(
                {"detail": "삭제 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        delete_post(post=post)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="posts_patch",
        summary="게시글 수정",
        description="작성자가 게시글을 부분 수정합니다.",
        request=PostPatchSerializer,
        responses={200: PostPatchResponseSerializer},
    )
    def patch(self, request: Request, post_id: int) -> Response:
        # 본인 글만
        post = get_object_or_404(Post, pk=post_id)

        user = request.user

        is_admin = getattr(user, "role", None) == "ADMIN"
        if post.author != user and not is_admin:
            return Response(
                {"detail": "수정 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PostPatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = patch_post(post=post, validated_data=serializer.validated_data)

        return Response(
            PostPatchResponseSerializer(post).data,
            status=status.HTTP_200_OK,
        )


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="posts_like",
        summary="게시글 좋아요",
        description="로그인 사용자가 게시글 좋아요를 추가한다.",
        responses={
            200: PostLikeResponseSerializer,
            401: OpenApiResponse(
                description="로그인 사용자가 아닐 경우",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="인증 필요",
                        value={"detail": "인증이 필요합니다."},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="게시글이 존재하지 않음",
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
        assert request.user.is_authenticated
        post = get_object_or_404(Post, pk=post_id)

        like_count = like_post(
            user=request.user,
            post=post,
        )

        data = {
            "post_id": post.pk,
            "liked": True,
            "like_count": like_count,
        }

        return Response(
            PostLikeResponseSerializer(data).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["커뮤니티"],
        operation_id="posts_unlike",
        summary="게시글 좋아요 취소",
        description="로그인 사용자가 게시글 좋아요를 취소한다.",
        responses={
            200: PostLikeResponseSerializer,
            401: OpenApiResponse(
                description="로그인 사용자가 아닐 경우",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="인증 필요",
                        value={"detail": "인증이 필요합니다."},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="게시글이 존재하지 않음",
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
    def delete(self, request: Request, post_id: int) -> Response:
        assert request.user.is_authenticated
        post = get_object_or_404(Post, pk=post_id)

        like_count = unlike_post(
            user=request.user,
            post=post,
        )

        data = {
            "post_id": post.pk,
            "liked": False,
            "like_count": like_count,
        }

        return Response(
            PostLikeResponseSerializer(data).data,
            status=status.HTTP_200_OK,
        )
