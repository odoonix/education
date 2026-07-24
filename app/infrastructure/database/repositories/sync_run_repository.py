from app.domain.entities.sync_run import SyncRun
from app.domain.entities.sync_log import SyncLog
from app.domain.ports.db_session import IDBConnection
from app.domain.repositories.sync_run_repository import SyncRunRepository
from app.infrastructure.database.models.sync_run import SyncRunModel
from app.infrastructure.database.models.sync_log import SyncLogModel


class SQLAlchemySyncRunRepository(SyncRunRepository):

    def __init__(self, db_connection: IDBConnection):
        self._db = db_connection

    def create(self, sync_run: SyncRun) -> SyncRun:
        session = self._db.get_session()
        try:
            model = self._to_run_model(sync_run)
            session.add(model)
            session.flush()
            sync_run.id = model.id
            session.commit()
            return sync_run
        finally:
            session.close()

    def finish(self, sync_run: SyncRun) -> None:
        session = self._db.get_session()
        try:
            model = session.get(SyncRunModel, sync_run.id)
            if model is None:
                return
            model.finished_at = sync_run.finished_at
            model.records_received = sync_run.records_received
            model.records_saved = sync_run.records_saved
            model.records_updated = sync_run.records_updated
            model.records_failed = sync_run.records_failed
            model.status = sync_run.status.value
            session.commit()
        finally:
            session.close()

    def add_log(self, sync_log: SyncLog) -> None:
        session = self._db.get_session()
        try:
            session.add(self._to_log_model(sync_log))
            session.commit()
        finally:
            session.close()

    @staticmethod
    def _to_run_model(sync_run: SyncRun) -> SyncRunModel:
        return SyncRunModel(
            operation_type=sync_run.operation_type,
            started_at=sync_run.started_at,
            status=sync_run.status.value,
            records_received=sync_run.records_received,
            records_saved=sync_run.records_saved,
            records_updated=sync_run.records_updated,
            records_failed=sync_run.records_failed,
            finished_at=sync_run.finished_at,
        )

    @staticmethod
    def _to_log_model(sync_log: SyncLog) -> SyncLogModel:
        return SyncLogModel(
            sync_run_id=sync_log.sync_run_id,
            level=sync_log.level.value,
            message=sync_log.message,
            odoo_id=sync_log.odoo_id,
        )
