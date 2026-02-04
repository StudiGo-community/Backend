from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any
from django.utils import timezone

from apps.accounts.models.attendance_record_model import AttendanceRecord

if TYPE_CHECKING:
    from apps.accounts.models.users import User


@dataclass
class DayAttendance:
    date: str
    day_name: str
    checked: bool
    is_today: bool
    is_future: bool


@dataclass
class WeeklyAttendance:
    week_start: str
    week_end: str
    today: str
    today_checked: bool
    days: list[DayAttendance]

    def to_dict(self) -> dict[str, Any]:
        return {
            "week_start": self.week_start,
            "week_end": self.week_end,
            "today": self.today,
            "today_checked": self.today_checked,
            "days": [
                {
                    "date": day.date,
                    "day_name": day.day_name,
                    "checked": day.checked,
                    "is_today": day.is_today,
                    "is_future": day.is_future,
                }
                for day in self.days
            ],
        }


class AttendanceService:
    DAY_NAMES: list[str] = ["월", "화", "수", "목", "금", "토", "일"]

    @classmethod
    def get_weekly_attendance(
        cls,
        user: User,
        target_date: date | None = None,
    ) -> WeeklyAttendance:
        if target_date is None:
            target_date = timezone.localdate()

        week_start = cls._get_week_start(target_date)
        week_end = week_start + timedelta(days=6)
        today = timezone.localdate()

        attendance_dates = cls._get_attendance_dates(user, week_start, week_end)

        days = [
            cls._create_day_attendance(
                week_start + timedelta(days=i),
                attendance_dates,
                today,
                i,
            )
            for i in range(7)
        ]

        return WeeklyAttendance(
            week_start=week_start.isoformat(),
            week_end=week_end.isoformat(),
            today=today.isoformat(),
            today_checked=today in attendance_dates,
            days=days,
        )

    @classmethod
    def is_today_checked(cls, user: User) -> bool:
        today = date.today()
        return AttendanceRecord.objects.filter(
            user=user,
            created_at__date=today,
        ).exists()

    @classmethod
    def _get_week_start(cls, target_date: date) -> date:
        return target_date - timedelta(days=target_date.weekday())

    @classmethod
    def _get_attendance_dates(
        cls,
        user: User,
        start: date,
        end: date,
    ) -> set[date]:
        records = AttendanceRecord.objects.filter(
            user=user,
            created_at__date__gte=start,
            created_at__date__lte=end,
        ).values_list("created_at__date", flat=True)

        return set(records)

    @classmethod
    def _create_day_attendance(
        cls,
        current_date: date,
        attendance_dates: set[date],
        today: date,
        day_index: int,
    ) -> DayAttendance:
        return DayAttendance(
            date=current_date.isoformat(),
            day_name=cls.DAY_NAMES[day_index],
            checked=current_date in attendance_dates,
            is_today=current_date == today,
            is_future=current_date > today,
        )
