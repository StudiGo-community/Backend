from django.db import models


class UserTimeStampedModel(models.Model):
    """
    유저 모델에 공통으로 사용되는 생성/수정 시간을 기록하는 추상 클래스.
    해당 클래스 상속 시 created_at, updated_at 필드를 갖게 됨.

    Meta:
        abstract = True

    이 클래스 자체는 데이터베이스 테이블을 생성하지 않고, 오직 다른 모델에 상속Mixin되는 용도로만 사용됨.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
