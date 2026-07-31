from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReadRecord[T]:
    raw_id: int | None
    value: T | None
    error: Exception | None = None

    @property
    def is_error(self) -> bool:
        return self.error is not None
