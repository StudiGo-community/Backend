from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PostsPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"
    page_size_query_param = None

    def get_paginated_response(self, data: Any) -> Response:
        return Response({"posts": data})


class CommentsPagination(PageNumberPagination):
    page_size = 15
    page_query_param = "page"
    page_size_query_param = None

    def get_paginated_response(self, data: Any) -> Response:
        return Response({"comments": data})
