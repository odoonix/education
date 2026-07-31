from __future__ import annotations

from dataclasses import dataclass

DEFAULT_PAGE_SIZE = 200
MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 1000


@dataclass(frozen=True, slots=True)
class PageSize:
    value: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        if not MIN_PAGE_SIZE <= self.value <= MAX_PAGE_SIZE:
            msg = f"page size must be between {MIN_PAGE_SIZE} and {MAX_PAGE_SIZE}"
            raise ValueError(msg)
