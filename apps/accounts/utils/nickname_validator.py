import re

from django.core.exceptions import ValidationError


NICK_RE = re.compile(r"^[A-Za-z0-9가-힣_.]{2,20}$")
RESERVED = {
    "admin",
    "administrator",
    "운영자",
    "관리자",
    "root",
    "system",
    "moderator",
    "staff",
}
KOR_BANNED_WORDS = {
    "씨발",
    "시발",
    "ㅅㅂ",
    "병신",
    "또라이",
    "개새",
    "개새끼",
    "좆",
    "썅",
    "염병",
    "꺼져",
}
EN_BANNED = {
    "fuck", "shit", "bitch", "asshole", "bastard",
    "nigger", "faggot",
}

_ASCII_RE = re.compile(r"[A-Za-z]")  # 영어 포함 여부 판단


def _contains_korean_badword(nickname: str) -> bool:
    # 한글 욕설 부분 포함 검사
    low = nickname.lower()
    return any(bad.lower() in low for bad in KOR_BANNED_WORDS)


def _english_profane(nickname: str) -> bool:
    low = nickname.lower()
    return any(word in low for word in EN_BANNED)


def validate_nickname(nickname: str) -> None:
    try:

        _ALT_AVAILABLE = True
    except Exception:
        _ALT_AVAILABLE = False

    """닉네임 유효성 검사"""
    if " " in nickname or nickname.strip() != nickname:
        raise ValidationError("닉네임에 공백은 사용할 수 없습니다.")

    if not NICK_RE.fullmatch(nickname):
        raise ValidationError("닉네임은 2~20자, 한글/영문/숫자/_/. 만 가능합니다.")

    if nickname.isdigit():
        raise ValidationError("숫자만으로는 사용할 수 없습니다.")

    if nickname.lower() in (s.lower() for s in RESERVED):
        raise ValidationError("사용할 수 없는 닉네임입니다.")

    if _contains_korean_badword(nickname) or _english_profane(nickname):
        raise ValidationError("부적절한 단어가 포함되어 사용할 수 없습니다.")
