from collections.abc import Generator
from fastapi import Depends
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.models.sync_run import SyncRun
from app.schemas.sync import SyncRunCreate


class SyncRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, skip: int = 0, limit: int = 50) -> list[SyncRun]:
        return (
            self.db.query(SyncRun)
            .order_by(SyncRun.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, sync_run_id: int) -> SyncRun | None:
        return self.db.get(SyncRun, sync_run_id)

    def create(self, payload: SyncRunCreate) -> SyncRun:
        sync_run = SyncRun(sync_type=payload.sync_type, sync_start_time=payload.sync_start_time ,sync_end_time=payload.sync_end_time ,fetched_records=payload.fetched_records ,stored_records= payload.stored_records ,updated_records=payload.updated_records ,error_records=payload.error_records ,sync_error=payload.sync_error,)
        self.db.add(sync_run)
        self.db.commit()
        self.db.refresh(sync_run)
        return sync_run
    
    def update(self, sync_run_id: int, payload: SyncRunCreate) -> SyncRun:
        sync_run = self.db.get(SyncRun, sync_run_id)

        sync_run.sync_type = payload.sync_type
        sync_run.sync_start_time = payload.sync_start_time
        sync_run.sync_end_time = payload.sync_end_time
        sync_run.fetched_records = payload.fetched_records
        sync_run.stored_records = payload.stored_records
        sync_run.updated_records = payload.updated_records
        sync_run.error_records = payload.error_records
        sync_run.sync_error = payload.sync_error
        self.db.commit()
        self.db.refresh(sync_run)

get_sync_run_repo = SyncRunRepository(db=get_db())