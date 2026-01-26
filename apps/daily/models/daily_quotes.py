from django.db import models

from apps.core.models import TimeStampedModel


class DailyQuote(TimeStampedModel):
    quote_date = models.DateField(unique=True)
    content = models.TextField()
    author = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "daily_quotes"

    def __str__(self) -> str:
        return f"{self.quote_date} {self.content}"
