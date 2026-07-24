import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import SyncLog, SyncRun

logger = logging.getLogger("sync")


class SyncRunLogger:
    def __init__(self, session: Session, operation_type: str):
        self.session = session
        self.sync_run = SyncRun(
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(self.sync_run)
        self.session.flush()
        logger.info(
            "sync run #%s started (operation_type=%s)",
            self.sync_run.id,
            operation_type,
        )
        self.sync_run_id = self.sync_run.id


    def log_info(self, message: str, entity_type: Optional[str] = None,
                 entity_odoo_id: Optional[int] = None) -> None:
        self._log("info", message, entity_type, entity_odoo_id)
        logger.info(message)

    def log_warning(self, message: str, entity_type: Optional[str] = None,
                     entity_odoo_id: Optional[int] = None) -> None:
        self._log("warning", message, entity_type, entity_odoo_id)
        logger.warning(message)

    def log_error(self, entity_type: str, entity_odoo_id: Optional[int],
                   message: str) -> None:
        self._log("error", message, entity_type, entity_odoo_id)
        logger.error(
            "error in %s (odoo_id=%s): %s", entity_type, entity_odoo_id, message
        )

    def _log(self, level: str, message: str, entity_type: Optional[str],
              entity_odoo_id: Optional[int]) -> None:
        log_row = SyncLog(
            sync_run_id=self.sync_run_id,
            level=level,
            entity_type=entity_type,
            entity_odoo_id=entity_odoo_id,
            error_message=message,
        )
        self.session.add(log_row)
        self.session.flush()


    def finish(self, status: str, stats: dict) -> None:
        self.sync_run.finished_at = datetime.now(timezone.utc)
        self.sync_run.received_count = stats.get("fetched", 0)
        self.sync_run.created_count = stats.get("created", 0)
        self.sync_run.updated_count = stats.get("updated", 0)
        self.sync_run.failed_count = stats.get("failed", 0)
        self.session.flush()
        logger.info(
            "sync run #%s ended (status=%s, stats=%s)",
            self.sync_run.id,
            status,
            stats,
        )
