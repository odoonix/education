from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class SyncType(StrEnum):
    FULL = "full"
    INCREMENTAL = "incremental"


class SyncStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UpsertResult(StrEnum):
    INSERTED = "inserted"
    UPDATED = "updated"
    UNCHANGED = "unchanged"


@dataclass(slots=True)
class SyncCounters:
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0

    def count_upsert(self, result: UpsertResult) -> None:
        if result is UpsertResult.INSERTED:
            self.inserted += 1
        elif result is UpsertResult.UPDATED:
            self.updated += 1
        else:
            self.unchanged += 1


@dataclass(frozen=True, slots=True)
class SyncRunSummary:
    run_id: int
    sync_type: SyncType
    status: SyncStatus
    started_at: datetime
    finished_at: datetime | None
    counters: SyncCounters
    lower_watermark: datetime | None
    upper_watermark: datetime | None
    fatal_error: str | None = None
