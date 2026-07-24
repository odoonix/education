from datetime import datetime
from typing import Protocol

from app.domain.entities.sync_run import SyncRun, SyncStatus
from app.domain.entities.sync_log import SyncLog, SyncLogLevel
from app.domain.repositories.sync_run_repository import SyncRunRepository


class SyncSource(Protocol):
    """Anything that can fetch and map records from the source system."""

    def sync(self) -> list: ...


class EntityRepository(Protocol):
    """Common shape of the per-entity repositories (upsert by odoo_id)."""

    def get_by_odoo_id(self, odoo_id: int): ...

    def save(self, entity) -> None: ...

    def update(self, entity) -> None: ...


class SyncEntityUseCase:
    """Synchronizes one entity type from the source into the database.

    Each record is processed independently: an error on one record is
    logged and counted, but never stops the rest of the batch.
    """

    def __init__(
        self,
        operation_type: str,
        source: SyncSource,
        repository: EntityRepository,
        sync_run_repository: SyncRunRepository,
    ):
        self._operation_type = operation_type
        self._source = source
        self._repository = repository
        self._sync_run_repository = sync_run_repository

    def execute(self) -> SyncRun:
        run = SyncRun(
            operation_type=self._operation_type,
            started_at=datetime.now(),
        )
        run = self._sync_run_repository.create(run)

        try:
            entities = self._source.sync()
        except Exception as exc:
            return self._fail_run(run, f"Failed to fetch from source: {exc}")

        run.records_received = len(entities)

        for entity in entities:
            try:
                if self._repository.get_by_odoo_id(entity.odoo_id) is None:
                    self._repository.save(entity)
                    run.records_saved += 1
                else:
                    self._repository.update(entity)
                    run.records_updated += 1
            except Exception as exc:
                run.records_failed += 1
                self._sync_run_repository.add_log(
                    SyncLog(
                        sync_run_id=run.id,
                        level=SyncLogLevel.ERROR,
                        message=str(exc),
                        odoo_id=getattr(entity, "odoo_id", None),
                    )
                )

        run.finished_at = datetime.now()
        run.status = self._resolve_status(run)
        self._sync_run_repository.finish(run)
        return run

    def _fail_run(self, run: SyncRun, message: str) -> SyncRun:
        self._sync_run_repository.add_log(
            SyncLog(
                sync_run_id=run.id,
                level=SyncLogLevel.ERROR,
                message=message,
            )
        )
        run.finished_at = datetime.now()
        run.status = SyncStatus.FAILED
        self._sync_run_repository.finish(run)
        return run

    @staticmethod
    def _resolve_status(run: SyncRun) -> SyncStatus:
        if run.records_failed == 0:
            return SyncStatus.SUCCESS
        if run.records_saved == 0 and run.records_updated == 0:
            return SyncStatus.FAILED
        return SyncStatus.PARTIAL
