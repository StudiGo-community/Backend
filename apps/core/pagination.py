from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PostsPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"
    page_size_query_param = None

    def get_paginated_response(self, data: Any) -> Response:
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "posts": data,
            }
        )