from typing import Any, TypedDict

from rest_framework import serializers

from apps.community.models.post_images import PostImage
from apps.community.models.posts import Post
from apps.community.serializers.comment_serializers import CommentResponseSerializer
from apps.community.serializers.common_serializers import AuthorSerializer
from apps.core.choices.community_choices import PostCategory


class PostImageInput(TypedDict):
    url: str
    order: int


class PostImageInputSerializer(serializers.Serializer[Any]):
    url = serializers.URLField()
    order = serializers.IntegerField(min_value=1)


class PostCreateSerializer(serializers.Serializer[Any]):
    title = serializers.CharField(min_length=1, max_length=100)
    content = serializers.CharField(min_length=1)
    category = serializers.ChoiceField(choices=PostCategory.choices)
    thumbnail_url = serializers.URLField(required=False, allow_null=True)
    images = PostImageInputSerializer(many=True, required=False, allow_empty=True)

    def validate_images(self, images: list[PostImageInput]) -> list[PostImageInput]:
        # order 중복 방지
        orders = [img["order"] for img in images]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("images.order 값이 중복되었습니다.")

        # 1부터 연속된 값인지 검증
        expected_orders = list(range(1, len(images) + 1))
        if sorted(orders) != expected_orders:
            raise serializers.ValidationError(
                "images.order 값은 1부터 연속된 숫자여야 합니다."
            )

        # url 중복 방지
        urls = [img["url"] for img in images]
        if len(urls) != len(set(urls)):
            raise serializers.ValidationError("images.url 값이 중복되었습니다.")
        return images

    def validate(self, attrs: Any) -> Any:
        images = attrs.get("images") or []
        thumbnail_url = attrs.get("thumbnail_url", None)

        # 이미지가 없을 때 썸네일 비허용
        if not images and thumbnail_url is not None:
            raise serializers.ValidationError(
                {
                    "thumbnail_url": "이미지가 있을 때만 thumbnail_url을 지정할 수 있습니다."
                }
            )

        if thumbnail_url is not None:
            image_urls = {img["url"] for img in images}
            if thumbnail_url not in image_urls:
                raise serializers.ValidationError(
                    {
                        "thumbnail_url": "thumbnail_url은 images에 포함된 url이어야 합니다."
                    }
                )
        return attrs


class PostImageResponseSerializer(serializers.ModelSerializer[PostImage]):
    class Meta:
        model = PostImage
        fields = ("id", "image_url", "sort_order")


class PostCreateResponseSerializer(serializers.ModelSerializer[Post]):
    author = AuthorSerializer(read_only=True)
    images = PostImageResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "category",
            "status",
            "thumbnail_url",
            "images",
            "like_count",
            "comment_count",
            "created_at",
        )


class PostPatchSerializer(serializers.Serializer[Any]):
    title = serializers.CharField(min_length=1, max_length=100, required=False)
    content = serializers.CharField(min_length=1, required=False)
    category = serializers.ChoiceField(choices=PostCategory.choices, required=False)
    thumbnail_url = serializers.URLField(required=False, allow_null=True)
    images = PostImageInputSerializer(many=True, required=False, allow_empty=True)

    def validate_images(self, images: list[PostImageInput]) -> list[PostImageInput]:
        # order 중복 방지
        orders = [img["order"] for img in images]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("images.order 값이 중복되었습니다.")

        # 1부터 연속된 값인지 검증
        expected_orders = list(range(1, len(images) + 1))
        if sorted(orders) != expected_orders:
            raise serializers.ValidationError(
                "images.order 값은 1부터 연속된 숫자여야 합니다."
            )

        # url 중복 방지
        urls = [img["url"] for img in images]
        if len(urls) != len(set(urls)):
            raise serializers.ValidationError("images.url 값이 중복되었습니다.")
        return images

    def validate(self, attrs: Any) -> Any:
        images = attrs.get("images")
        thumbnail_url = attrs.get("thumbnail_url", None)

        if images is not None:
            if not images and thumbnail_url is not None:
                raise serializers.ValidationError(
                    {
                        "thumbnail_url": "이미지가 있을 때만 thumbnail_url을 지정할 수 있습니다."
                    }
                )

            if thumbnail_url is not None:
                image_urls = {img["url"] for img in images}
                if thumbnail_url not in image_urls:
                    raise serializers.ValidationError(
                        {
                            "thumbnail_url": "thumbnail_url은 images에 포함된 url이어야 합니다."
                        }
                    )
        return attrs


class PostPatchResponseSerializer(serializers.ModelSerializer[Post]):
    images = PostImageResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "category",
            "thumbnail_url",
            "images",
            "updated_at",
        )


class PostListItemSerializer(serializers.ModelSerializer[Post]):
    author = AuthorSerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    images = PostImageResponseSerializer(many=True, read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content_preview",
            "category",
            "blinded_reason",
            "author",
            "thumbnail_url",
            "images",
            "like_count",
            "comment_count",
            "view_count",
            "is_liked",
            "updated_at",
        )

    def get_content_preview(self, post: Post) -> str:
        max_length = 100
        content = post.content or ""
        content = content.strip().replace("\n", " ")

        if len(content) <= max_length:
            return content
        return content[:max_length].rstrip() + "…"


class PostDetailResponseSerializer(serializers.ModelSerializer[Post]):
    author = AuthorSerializer(read_only=True)
    images = PostImageResponseSerializer(many=True, read_only=True)
    comments = CommentResponseSerializer(many=True, read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "category",
            "author",
            "thumbnail_url",
            "images",
            "like_count",
            "comment_count",
            "view_count",
            "is_liked",
            "created_at",
            "updated_at",
            "comments",
        )


class PostLikeResponseSerializer(serializers.Serializer[Any]):
    post_id = serializers.IntegerField(read_only=True)
    liked = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
