from typing import Any

from rest_framework import serializers


class AuthorSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    nickname = serializers.CharField(allow_blank=True, required=False)
    profile_image_url = serializers.CharField(allow_null=True, required=False)
