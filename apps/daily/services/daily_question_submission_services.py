from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException

from apps.daily.models.daily_questions import DailyQuestion
from apps.daily.models.daily_question_submissions import DailyQuestionSubmission

User = get_user_model()


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
    # 비교 기준 통일: 양 끝 공백 제거 + 대문자
    return text.strip().upper()


def _mark_attendance_if_needed(*, user: User, today: timezone.datetime) -> None:
    """
    '제출 즉시 자동 출석체크' 훅.
    프로젝트 출석 모델/서비스가 뭔지 몰라서 자리만 만들어둠.
    """
    # 예시(실제 구현은 너희 attendance 앱에 맞게):
    # AttendanceService.check_in(user=user, date=today.date())
    return


@transaction.atomic
def submit_today_question(
    *,
    user: User,
    submitted_answer_text: str,
) -> SubmissionResult:
    """
    - 오늘의 DailyQuestion 조회
    - 중복 제출 방지(유니크 + select_for_update)
    - 정답 비교 후 저장
    - 제출 성공 시 출석체크 훅 호출
    """
    today_date = timezone.localdate()

    # 오늘 문제 행을 잠금 (동시성 방어)
    daily_question: Optional[DailyQuestion] = (
        DailyQuestion.objects.select_for_update()
        .select_related("question")
        .filter(question_date=today_date, is_active=True)
        .first()
    )
    if daily_question is None:
        raise TodayQuestionNotFoundError()

    correct_answer_raw = daily_question.question.answer_text
    correct_answer = _normalize_answer(correct_answer_raw or "")
    user_answer = _normalize_answer(submitted_answer_text)

    is_correct = (correct_answer != "") and (user_answer == correct_answer)

    try:
        submission = DailyQuestionSubmission.objects.create(
            daily_question=daily_question,
            user=user,
            submitted_answer_text=submitted_answer_text,
            is_correct=is_correct,
        )
    except IntegrityError as e:
        # 유니크 제약으로 중복 제출이 잡힘
        raise AlreadySubmittedError() from e

    _mark_attendance_if_needed(user=user, today=timezone.now())

    return SubmissionResult(submission=submission)