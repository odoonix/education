from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SyncStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass
class SyncRun:
    operation_type: str
    started_at: datetime
    status: SyncStatus = SyncStatus.RUNNING
    records_received: int = 0
    records_saved: int = 0
    records_updated: int = 0
    records_failed: int = 0
    finished_at: datetime | None = None
    id: int | None = None
