from django.db import models

from apps.core.enumeration.community_enumerations import ReportStatus


class TimeStampedModel(models.Model):
    """
    모든 모델에 공통으로 사용되는 생성/수정 시간을 기록하는 추상 클래스
    이 클래스를 상속받는 모든 모델은 created_at, updated_at 필드를 자동으로 갖게됩니다.

    Meta:
        abstract = True: 이 클래스 자체는 데이터베이스 테이블을 생성하지 않으며, 오직 다른 모델에 상속(Mixin)되는 용도로만 사용됩니다.
    """

    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시 자동 기록
    updated_at = models.DateTimeField(auto_now=True)  # 저장될 때 자동 갱신

    class Meta:
        abstract = True  # 테이블을 생성하지 않음


class VerificationTimeStampedModel(models.Model):
    """
    인증번호를 발송할 시 사용되는 만료/생성 시간을 기록하는 추상 클래스
    이 클래스를 상속받는 모든 모델은 created_at, expires_at 필드를 자동으로 갖게 됩니다.

    Meta:
        abstract = True:  클래스 자체는 데이터베이스 테이블을 생성하지 않으며, 오직 다른 모델에 상속(Mixin)되는 용도로만 사용됩니다.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class BaseReport(models.Model):
    reporter = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
    )
    reason = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
