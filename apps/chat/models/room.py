from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=50) # 채팅방 이름
    description = models.CharField(max_length=200) # 채팅방 설명 (해시태그)
    participant_count = models.IntegerField(default=0) # 채팅방 인원 수
    last_message_at = models.DateTimeField(auto_now=True) # 마지막 메세지 시각

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

