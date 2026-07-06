# repos/sync_run_repository.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.orm_models import SyncRun
from repos.base_repository import BaseRepository

class SyncRunRepository(BaseRepository[SyncRun]):
    def __init__(self, db: Session):
        super().__init__(SyncRun, db)
    
    def create_run(self) -> SyncRun:
        """Create a new sync run record"""
        sync_run = SyncRun(status="running")
        self.db.add(sync_run)
        self.db.commit()
        self.db.refresh(sync_run)
        return sync_run
    
    def complete_run(self, sync_run: SyncRun, 
                     contacts_count: int = 0,
                     products_count: int = 0,
                     sale_orders_count: int = 0,
                     error_count: int = 0) -> SyncRun:
        """Mark a sync run as completed"""
        sync_run.status = "completed"
        sync_run.finished_at = datetime.utcnow()
        sync_run.contacts_count = contacts_count
        sync_run.products_count = products_count
        sync_run.sale_orders_count = sale_orders_count
        sync_run.error_count = error_count
        self.db.commit()
        self.db.refresh(sync_run)
        return sync_run
    
    def fail_run(self, sync_run: SyncRun, error_message: str = None) -> SyncRun:
        """Mark a sync run as failed"""
        sync_run.status = "failed"
        sync_run.finished_at = datetime.utcnow()
        if error_message:
            sync_run.log_details = error_message
        self.db.commit()
        self.db.refresh(sync_run)
        return sync_run
    
    def get_last_run(self) -> Optional[SyncRun]:
        """Get the most recent sync run"""
        return self.db.query(SyncRun).order_by(
            SyncRun.id.desc()
        ).first()
    
    def get_runs_by_status(self, status: str) -> List[SyncRun]:
        """Get all sync runs with specific status"""
        return self.db.query(SyncRun).filter(
            SyncRun.status == status
        ).all()