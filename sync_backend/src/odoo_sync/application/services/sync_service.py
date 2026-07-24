from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TypeVar

from odoo_sync.application.ports.erp import ErpReader
from odoo_sync.application.ports.unit_of_work import UnitOfWork, UnitOfWorkFactory
from odoo_sync.application.services.payload_sanitizer import sanitize_error
from odoo_sync.application.services.shutdown import ShutdownFlag
from odoo_sync.domain.exceptions import MissingReferenceError
from odoo_sync.domain.models import Contact, Product, SaleOrder, SaleOrderLine
from odoo_sync.domain.read_outcome import ReadRecord
from odoo_sync.domain.sync import SyncCounters, SyncRunSummary, SyncStatus, SyncType, UpsertResult

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class SyncService:
    erp: ErpReader
    uow_factory: UnitOfWorkFactory
    logger: logging.Logger
    shutdown: ShutdownFlag
    sync_lock: SyncLock

    def sync(
        self,
        *,
        sync_type: SyncType,
        page_size: int,
    ) -> SyncRunSummary:
        with self.sync_lock.acquire():
            return self._sync_locked(
                sync_type=sync_type,
                page_size=page_size,
            )

    def _sync_locked(
        self,
        *,
        sync_type: SyncType,
        page_size: int,
    ) -> SyncRunSummary:
        started = datetime.now(UTC)
        counters = SyncCounters()

        lower, upper = self._watermarks(sync_type)
        run_id = self._start_run(
            sync_type,
            lower,
            upper,
            started,
        )

        status = SyncStatus.SUCCESS
        fatal: str | None = None

        self.logger.info(
            "sync started",
            extra={
                "sync_type": sync_type.value,
                "run_id": run_id,
            },
        )

        try:
            self._process(
                "contact",
                self.erp.iter_contacts(
                    page_size=page_size,
                    lower=lower,
                    upper=upper,
                ),
                counters,
                run_id,
                self._persist_contact,
            )

            self._process(
                "product",
                self.erp.iter_products(
                    page_size=page_size,
                    lower=lower,
                    upper=upper,
                ),
                counters,
                run_id,
                self._persist_product,
            )

            self._process(
                "sale_order",
                self.erp.iter_sale_orders(
                    page_size=page_size,
                    lower=lower,
                    upper=upper,
                ),
                counters,
                run_id,
                self._persist_sale_order,
            )

            self._process(
                "sale_order_line",
                self.erp.iter_sale_order_lines(
                    page_size=page_size,
                    lower=lower,
                    upper=upper,
                ),
                counters,
                run_id,
                self._persist_sale_order_line,
            )

            if self.shutdown.cancelled:
                status = SyncStatus.CANCELLED

        except Exception as exc:
            status = SyncStatus.FAILED
            fatal = sanitize_error(exc)

            self.logger.error(
                "sync fatal failure",
                extra={
                    "run_id": run_id,
                    "error": fatal,
                },
            )

        finished = datetime.now(UTC)

        self._finish_run(
            run_id,
            status,
            finished,
            counters,
            fatal,
        )

        return SyncRunSummary(
            run_id,
            sync_type,
            status,
            started,
            finished,
            counters,
            lower,
            upper,
            fatal,
        )

    def _watermarks(self, sync_type: SyncType) -> tuple[datetime | None, datetime | None]:
        if sync_type is SyncType.FULL:
            return None, self.erp.get_upper_watermark()
        with self.uow_factory() as uow:
            lower = uow.sync_runs.latest_success_upper_watermark()
        if lower is None:
            msg = "incremental sync requires a prior successful full or incremental sync"
            raise RuntimeError(msg)
        return lower, self.erp.get_upper_watermark()

    def _start_run(
        self,
        sync_type: SyncType,
        lower: datetime | None,
        upper: datetime | None,
        started: datetime,
    ) -> int:
        with self.uow_factory() as uow:
            run_id = uow.sync_runs.start(
                sync_type=sync_type,
                lower_watermark=lower,
                upper_watermark=upper,
                started_at=started,
            )
            uow.commit()
            return run_id

    def _finish_run(
        self,
        run_id: int,
        status: SyncStatus,
        finished: datetime,
        counters: SyncCounters,
        fatal: str | None,
    ) -> None:
        with self.uow_factory() as uow:
            uow.sync_runs.finish(
                run_id,
                status=status,
                finished_at=finished,
                counters=counters,
                fatal_error=fatal,
            )
            uow.commit()
        self.logger.info(
            "sync finished",
            extra={"run_id": run_id, "status": status.value, "failed_count": counters.failed},
        )

    def _process(
        self,
        entity_type: str,
        records: Iterable[ReadRecord[T]],
        counters: SyncCounters,
        run_id: int,
        persist: Callable[[UnitOfWork, T], UpsertResult],
    ) -> None:
        self.logger.info("entity processing started", extra={"entity_type": entity_type})
        for record in records:
            if self.shutdown.cancelled:
                return
            counters.fetched += 1
            if record.is_error:
                counters.failed += 1
                self._log_record_error(run_id, entity_type, record.raw_id, "map", record.error)
                continue
            assert record.value is not None
            try:
                with self.uow_factory() as uow:
                    result = persist(uow, record.value)
                    uow.commit()
                counters.count_upsert(result)
            except Exception as exc:
                counters.failed += 1
                self._log_record_error(run_id, entity_type, record.raw_id, "upsert", exc)

    def _log_record_error(
        self,
        run_id: int,
        entity_type: str,
        odoo_id: int | None,
        operation: str,
        exc: BaseException | None,
    ) -> None:
        error = exc or RuntimeError("unknown record error")
        message = sanitize_error(error)
        self.logger.warning(
            "record sync failure",
            extra={"entity_type": entity_type, "odoo_id": odoo_id, "error": message},
        )
        with self.uow_factory() as uow:
            uow.sync_logs.add(
                sync_run_id=run_id,
                entity_type=entity_type,
                odoo_id=odoo_id,
                attempted_operation=operation,
                error_type=type(error).__name__,
                error_message=message,
            )
            uow.commit()

    @staticmethod
    def _persist_contact(uow: UnitOfWork, contact: Contact) -> UpsertResult:
        return uow.contacts.upsert(contact)

    @staticmethod
    def _persist_product(uow: UnitOfWork, product: Product) -> UpsertResult:
        return uow.products.upsert(product)

    @staticmethod
    def _persist_sale_order(uow: UnitOfWork, order: SaleOrder) -> UpsertResult:
        customer_id = uow.contacts.find_id_by_odoo_id(order.customer_odoo_id)
        if customer_id is None:
            raise MissingReferenceError(f"missing contact odoo_id={order.customer_odoo_id}")
        return uow.sale_orders.upsert(order, customer_id=customer_id)

    @staticmethod
    def _persist_sale_order_line(uow: UnitOfWork, line: SaleOrderLine) -> UpsertResult:
        sale_order_id = uow.sale_orders.find_id_by_odoo_id(line.sale_order_odoo_id)
        product_id = uow.products.find_id_by_odoo_id(line.product_odoo_id)
        if sale_order_id is None:
            raise MissingReferenceError(f"missing sale order odoo_id={line.sale_order_odoo_id}")
        if product_id is None:
            raise MissingReferenceError(f"missing product odoo_id={line.product_odoo_id}")
        return uow.sale_order_lines.upsert(line, sale_order_id=sale_order_id, product_id=product_id)
