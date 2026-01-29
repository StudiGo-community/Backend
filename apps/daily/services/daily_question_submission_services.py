from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, cast

from django.contrib.auth.models import AbstractBaseUser
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException

from apps.daily.models.daily_question_submissions import DailyQuestionSubmission
from apps.daily.models.daily_questions import DailyQuestion


class AlreadySubmittedError(APIException):
    status_code = 409
    default_detail = "이미 오늘의 문제를 제출했습니다."
    default_code = "already_submitted"


class TodayQuestionNotFoundError(APIException):
    status_code = 404
    default_detail = "오늘의 문제가 존재하지 않습니다."
    default_code = "today_question_not_found"


@dataclass(frozen=True)
class SubmissionResult:
    submission: DailyQuestionSubmission


def _normalize_answer(text: str) -> str:
    return text.strip().upper()


def _mark_attendance_if_needed(
    *,
    user: AbstractBaseUser,
    today: datetime,
) -> None:
    return


@transaction.atomic
def submit_today_question(
    *,
    user: AbstractBaseUser,
    submitted_answer_text: str,
) -> SubmissionResult:
    today_date = timezone.localdate()

    daily_question: Optional[DailyQuestion] = (
        cast(Any, DailyQuestion)
        .objects.select_for_update()
        .select_related("question")
        .filter(question_date=today_date, is_active=True)
        .first()
    )
    if daily_question is None:
        raise TodayQuestionNotFoundError()

    correct_answer_raw = daily_question.question.answer_text
    correct_answer = _normalize_answer(correct_answer_raw or "")
    user_answer = _normalize_answer(submitted_answer_text)

    is_correct = bool(correct_answer) and (user_answer == correct_answer)

    try:
        submission = cast(Any, DailyQuestionSubmission).objects.create(
            daily_question=daily_question,
            user=user,
            submitted_answer_text=submitted_answer_text,
            is_correct=is_correct,
        )
    except IntegrityError as e:
        raise AlreadySubmittedError() from e

    _mark_attendance_if_needed(
        user=user,
        today=timezone.now(),
    )

    return SubmissionResult(submission=submission)
