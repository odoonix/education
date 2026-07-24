from sqlalchemy import func
from sqlalchemy.orm import Session

from models.sync_runs import SyncRun


class SyncRunRepository:
    def __init__(self, session: Session):
        self._session = session

    def start(self, operation_type: str) -> SyncRun:
        run = SyncRun(
            operation_type=operation_type,
            records_fetched=0,
            records_created=0,
            records_updated=0,
            errors_count=0,
            status="running",
        )
        self._session.add(run)
        self._session.flush()
        return run

    def finish(self, run: SyncRun, status: str) -> None:
        run.finished_at = func.now()
        run.status = status
        self._session.flush()