from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder


from app.core.database import get_db
from app.models.sync_run import SyncLog
from app.schemas.sync import SyncLogCreate


class SyncLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, skip: int = 0, limit: int = 50) -> list[SyncLog]:
        return (
            self.db.query(SyncLog)
            .order_by(SyncLog.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, sync_log_id: int) -> SyncLog | None:
        return self.db.get(SyncLog, sync_log_id)

    def create(self, payload: SyncLogCreate) -> SyncLog:
        sync_log = SyncLog(sync_run_id=payload.sync_run_id, level=payload.level ,message=payload.message ,data=jsonable_encoder(payload.data))
        self.db.add(sync_log)
        self.db.commit()
        self.db.refresh(sync_log)
        return sync_log
