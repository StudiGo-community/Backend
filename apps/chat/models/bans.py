from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.core.models import TimeStampedModel


class Bans(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="bans",
    )  # 유저 ID

    room = models.ForeignKey(
        "Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="bans"
    )  # 방 ID / null 이면 전체 차단

    ends_at = models.DateTimeField(null=True, blank=True)  # null 이면 영구
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "chat_bans"
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["room", "is_active"]),
        ]
        constraints = [
            # 특정 방 차단 (활성화시 user/room 중복 방지)
            models.UniqueConstraint(
                fields=["user", "room"],
                condition=Q(is_active=True) & Q(room__isnull=False),
                name="unique_bans",
            ),
            # 전체 방 차단 (활성 상태에서 user당 id 1개 허용)
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_active=True) & Q(room__isnull=True),
                name="unique_bans_user",
            ),
        ]

    def __str__(self) -> str:
        scope = "GLOBAL" if self.room is None else f"ROOM:{self.room}"
        return f"user={self.user} scope={scope} active={self.is_active} ends_at={self.ends_at}"
