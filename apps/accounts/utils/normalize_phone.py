from __future__ import annotations

import re

PHONE_RE = re.compile(r"\D+")


def normalize_phone(phone: str) -> str:
    # 숫자만 남기기 (ex: 010-1234-5678 -> 01012345678)
    return PHONE_RE.sub("", phone or "").strip()
