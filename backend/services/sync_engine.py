
import logging
from typing import Callable

from sqlalchemy.orm import Session

from repositories.sync_run_repository import SyncRunRepository
from repositories.sync_log_repository import SyncLogRepository

logger = logging.getLogger(__name__)


class SyncEngine:
    def __init__(
        self,
        session: Session,
        operation_type: str,
        count_fn: Callable[[], int],
        fetch_page_fn: Callable[[int, int], list[dict]],
        map_fn: Callable[[dict], object],
        upsert_fn: Callable[[object], tuple[int, bool]],
        batch_size: int = 500,
        shutdown_handler=None,   # <- جدید
    ):
        self._session = session
        self._operation_type = operation_type
        self._count_fn = count_fn
        self._fetch_page_fn = fetch_page_fn
        self._map_fn = map_fn
        self._upsert_fn = upsert_fn
        self._batch_size = batch_size
        self._shutdown_handler = shutdown_handler
        self._sync_run_repo = SyncRunRepository(session)
        self._sync_log_repo = SyncLogRepository(session)

    def run(self) -> dict:
        run = self._sync_run_repo.start(self._operation_type)
        self._session.commit()

        total = self._count_fn()
        logger.info("sync_started", extra={"operation": self._operation_type, "total_records": total})

        records_fetched = 0
        records_created = 0
        records_updated = 0
        errors_count = 0

        offset = 0
        while offset < total:
            batch = self._fetch_page_fn(offset, self._batch_size)
            if not batch:
                break

            for raw in batch:
                records_fetched += 1
                record_ref = str(raw.get("id", "unknown"))

                try:
                    with self._session.begin_nested():
                        entity = self._map_fn(raw)
                        _, created = self._upsert_fn(entity)

                    if created:
                        records_created += 1
                    else:
                        records_updated += 1

                except Exception as exc:
                    errors_count += 1
                    logger.error(
                        "record_sync_failed",
                        extra={"operation": self._operation_type, "record_id": record_ref, "error": str(exc)},
                    )
                    self._sync_log_repo.add(
                        sync_run_id=run.id,
                        level="ERROR",
                        message=str(exc),
                        record_reference=record_ref,
                    )

            self._session.commit()
            offset += self._batch_size
            logger.info(
                "sync_progress",
                extra={"operation": self._operation_type, "processed": min(offset, total), "total": total},
            )

            if self._shutdown_handler and self._shutdown_handler.shutdown_requested:
                logger.warning(
                    "sync_interrupted_gracefully",
                    extra={"operation": self._operation_type, "processed": min(offset, total), "total": total},
                )
                status = "interrupted"
                run.records_fetched = records_fetched
                run.records_created = records_created
                run.records_updated = records_updated
                run.errors_count = errors_count
                self._sync_run_repo.finish(run, status)
                self._session.commit()
                return {
                    "operation": self._operation_type,
                    "records_fetched": records_fetched,
                    "records_created": records_created,
                    "records_updated": records_updated,
                    "errors_count": errors_count,
                    "status": status,
                }

        status = "success" if errors_count == 0 else "completed_with_errors"

        run.records_fetched = records_fetched
        run.records_created = records_created
        run.records_updated = records_updated
        run.errors_count = errors_count
        self._sync_run_repo.finish(run, status)
        self._session.commit()

        summary = {
            "operation": self._operation_type,
            "records_fetched": records_fetched,
            "records_created": records_created,
            "records_updated": records_updated,
            "errors_count": errors_count,
            "status": status,
        }
        logger.info("sync_finished", extra=summary)
        return summary