from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=50)  # 채팅방 이름
    description = models.CharField(
        max_length=200, null=True, blank=True
    )  # 채팅방 설명 (해시태그)
    participant_count = models.IntegerField()  # 채팅방 인원 수
    updated_at = models.DateTimeField(
        null=True, default=None
    )  # 마지막 메세지 시각

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} {self.description} {self.participant_count}"
