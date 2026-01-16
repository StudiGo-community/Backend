from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.post_serializers import (
    PostCreateResponseSerializer,
    PostCreateSerializer,
)
from apps.community.services.post_services import create_post


class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
