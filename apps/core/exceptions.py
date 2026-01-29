from __future__ import annotations

from typing import Any, Optional

from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Optional[Response]:
    response: Response | None = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data

    # 이미 {"detail": "..."}면 그대로
    if isinstance(data, dict) and "detail" in data and isinstance(data["detail"], str):
        return response

    # dict(필드 에러들) -> 첫 에러 메시지만 뽑아서 detail로 통일
    message = "요청값이 올바르지 않습니다."
    if isinstance(data, dict):
        # 예: {"phone": ["msg"]} 또는 {"phone": {"detail": "msg"}}
        for _, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], str):
                message = v[0]
                break
            if isinstance(v, dict):
                # {"detail": "..."} or {"non_field_errors": ["..."]}
                if "detail" in v and isinstance(v["detail"], str):
                    message = v["detail"]
                    break
                for _, vv in v.items():
                    if isinstance(vv, list) and vv and isinstance(vv[0], str):
                        message = vv[0]
                        break
            if isinstance(v, str):
                message = v
                break

    response.data = {"detail": message}
    return response
