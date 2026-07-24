from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SyncLogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class SyncLog:
    sync_run_id: int
    level: SyncLogLevel
    message: str
    odoo_id: int | None = None
    created_at: datetime | None = None
    id: int | None = None
