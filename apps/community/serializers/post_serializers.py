from typing import Any, TypedDict

from rest_framework import serializers

from apps.community.models.post_images import PostImage
from apps.community.models.posts import Post
from apps.core.enumeration.community_enumerations import PostCategory


class PostImageInput(TypedDict):
    url: str
    order: int


class PostImageInputSerializer(serializers.Serializer[Any]):
    url = serializers.URLField()
    order = serializers.IntegerField(min_value=1)

    def validate(self, attrs: PostImageInput) -> PostImageInput:
        # url 중복 방지(같은 url 여러 번 들어오는 경우)
        return attrs


class PostCreateSerializer(serializers.Serializer[Any]):
    title = serializers.CharField(min_length=1, max_length=100)
    content = serializers.CharField(min_length=1)
    category = serializers.ChoiceField(choices=PostCategory.choices)
    thumbnail_url = serializers.URLField(required=False, allow_null=True)
    images = PostImageInputSerializer(many=True, required=False)

    def validate_images(self, images: list[PostImageInput]) -> list[PostImageInput]:
        # order 중복 방지
        orders = [img["order"] for img in images]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("images.order 값이 중복되었습니다.")
        # url 중복 방지
        urls = [img["url"] for img in images]
        if len(urls) != len(set(urls)):
            raise serializers.ValidationError("images.url 값이 중복되었습니다.")
        return images

    def validate(self, attrs: Any) -> Any:
        images = attrs.get("images") or []
        thumbnail_url = attrs.get("thumbnail_url", None)

        if thumbnail_url is not None:
            image_urls = {img["url"] for img in images}
            if thumbnail_url not in image_urls:
                raise serializers.ValidationError(
                    {
                        "thumbnail_url": "thumbnail_url은 images에 포함된 url이어야 합니다."
                    }
                )
        return attrs


class PostAuthorSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    nickname = serializers.CharField(allow_blank=True, required=False)
    profile_image_url = serializers.CharField(allow_null=True, required=False)


class PostImageResponseSerializer(serializers.ModelSerializer[PostImage]):
    class Meta:
        model = PostImage
        fields = ("id", "image_url", "sort_order")


class PostCreateResponseSerializer(serializers.ModelSerializer[Post]):
    author = serializers.SerializerMethodField()
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

    def get_author(self, obj: Post) -> dict[str, Any]:
        author = obj.author
        return {
            "id": author.id,
            "nickname": getattr(author, "nickname", "") or "",
            "profile_image_url": getattr(author, "profile_image_url", None),
        }
