from django.db import models

from apps.accounts.models.user import User


class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_record"
        """
        출석: 하루 1회 허용
        """
        constraints = [
            models.UniqueConstraint(
                fields=["user", "created_date"],
                name="attendance_record_once_per_day",
            )
        ]
