from rest_framework import serializers


class DailyQuoteResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    quotes = serializers.DictField(
        child=serializers.CharField()
    )
    refreshed_at = serializers.DateTimeField()