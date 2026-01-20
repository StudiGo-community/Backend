from typing import cast, Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from apps.community.serializers.post_serializers import (
    PostCreateResponseSerializer,
    PostCreateSerializer,
    PostListItemSerializer,
)
from apps.community.services.post_services import create_post, get_post_list
from apps.core.enumeration.community_enumerations import PostCategory
from apps.core.enumeration.parameter_enumeration import SearchField, Sort
from apps.core.pagination import PostsPagination


class PostCreateListAPIView(APIView):
    def get_permissions(self) -> Any:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return []

    @extend_schema(
        tags=["Posts"],
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
        )

        return Response(
            PostCreateResponseSerializer(post).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Posts"],
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
