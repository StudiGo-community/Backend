from dataclasses import dataclass
from typing import Mapping, Sequence, TypeAlias

# DRF ValidationError(detail=...)에서 안전한 값 타입 (bool 금지)
APIExceptionInput: TypeAlias = (
    str | Sequence["APIExceptionInput"] | Mapping[str, "APIExceptionInput"]
)


@dataclass(frozen=True)
class AuthServiceError(Exception):
    detail: APIExceptionInput
