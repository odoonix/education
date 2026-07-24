from sqlalchemy.orm import Session

from models.sync_logs import SyncLog


class SyncLogRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, sync_run_id: int, level: str, message: str, record_reference: str | None = None) -> None:
        log = SyncLog(
            sync_run_id=sync_run_id,
            level=level,
            message=message,
            record_reference=record_reference,
        )
        self._session.add(log)