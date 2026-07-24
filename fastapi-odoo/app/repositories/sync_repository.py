from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.sync import (
    SyncLog,
    SyncRun,
    SyncStatus,
)


class SyncRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_run(self) -> SyncRun:
        sync_run = SyncRun(
            status=SyncStatus.RUNNING,
        )

        self._session.add(sync_run)
        self._session.flush()

        return sync_run

    def complete_run(
        self,
        sync_run: SyncRun,
    ) -> None:
        sync_run.status = SyncStatus.SUCCESS
        sync_run.finished_at = datetime.now(timezone.utc)

    def fail_run(
        self,
        sync_run: SyncRun,
        error_message: str,
    ) -> None:
        sync_run.status = SyncStatus.FAILED
        sync_run.finished_at = datetime.now(timezone.utc)
        sync_run.error_message = error_message

    def create_log(
        self,
        sync_run: SyncRun,
        level: str,
        message: str,
        entity: str | None = None,
        action: str | None = None,
        record_odoo_id: int | None = None,
    ) -> SyncLog:
        log = SyncLog(
            sync_run=sync_run,
            level=level,
            entity=entity,
            action=action,
            record_odoo_id=record_odoo_id,
            message=message,
        )

        self._session.add(log)

        return log