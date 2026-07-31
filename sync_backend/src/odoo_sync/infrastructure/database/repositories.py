from __future__ import annotations

from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from odoo_sync.domain.models import Contact, Product, SaleOrder, SaleOrderLine
from odoo_sync.domain.sync import SyncCounters, SyncStatus, SyncType, UpsertResult
from odoo_sync.infrastructure.database.models import (
    ContactModel,
    ProductModel,
    SaleOrderLineModel,
    SaleOrderModel,
    SyncLogModel,
    SyncRunModel,
)

ModelT = TypeVar("ModelT")


class UpsertMixin[ModelT]:
    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_id_by_odoo_id(self, odoo_id: int) -> int | None:
        return self.session.scalar(select(self.model.id).where(self.model.odoo_id == odoo_id))  # type: ignore[attr-defined]

    def _upsert(self, odoo_id: int, values: dict[str, Any]) -> UpsertResult:
        existing = self.session.scalar(select(self.model).where(self.model.odoo_id == odoo_id))  # type: ignore[attr-defined]
        if existing is None:
            self.session.add(self.model(odoo_id=odoo_id, **values))  # type: ignore[call-arg]
            return UpsertResult.INSERTED
        changed = {
            name: value for name, value in values.items() if getattr(existing, name) != value
        }
        if not changed:
            return UpsertResult.UNCHANGED
        for name, value in changed.items():
            setattr(existing, name, value)
        return UpsertResult.UPDATED


class SqlContactRepository(UpsertMixin[ContactModel]):
    model = ContactModel

    def upsert(self, contact: Contact) -> UpsertResult:
        return self._upsert(
            contact.odoo_id,
            {
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "mobile": contact.mobile,
                "odoo_write_date": contact.odoo_write_date,
            },
        )


class SqlProductRepository(UpsertMixin[ProductModel]):
    model = ProductModel

    def upsert(self, product: Product) -> UpsertResult:
        return self._upsert(
            product.odoo_id,
            {
                "name": product.name,
                "internal_reference": product.internal_reference,
                "sale_price": product.sale_price,
                "product_type": product.product_type,
                "odoo_write_date": product.odoo_write_date,
            },
        )


class SqlSaleOrderRepository(UpsertMixin[SaleOrderModel]):
    model = SaleOrderModel

    def upsert(self, order: SaleOrder, *, customer_id: int) -> UpsertResult:
        return self._upsert(
            order.odoo_id,
            {
                "order_number": order.order_number,
                "customer_id": customer_id,
                "order_date": order.order_date,
                "state": order.state,
                "total_amount": order.total_amount,
                "odoo_write_date": order.odoo_write_date,
            },
        )


class SqlSaleOrderLineRepository(UpsertMixin[SaleOrderLineModel]):
    model = SaleOrderLineModel

    def upsert(self, line: SaleOrderLine, *, sale_order_id: int, product_id: int) -> UpsertResult:
        return self._upsert(
            line.odoo_id,
            {
                "sale_order_id": sale_order_id,
                "product_id": product_id,
                "quantity": line.quantity,
                "unit_price": line.unit_price,
                "subtotal": line.subtotal,
                "odoo_write_date": line.odoo_write_date,
            },
        )


class SqlSyncRunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def start(
        self,
        *,
        sync_type: SyncType,
        lower_watermark: datetime | None,
        upper_watermark: datetime | None,
        started_at: datetime,
    ) -> int:
        run = SyncRunModel(
            sync_type=sync_type.value,
            status=SyncStatus.RUNNING.value,
            started_at=started_at,
            lower_watermark=lower_watermark,
            upper_watermark=upper_watermark,
        )
        self.session.add(run)
        self.session.flush()
        return run.id

    def finish(
        self,
        run_id: int,
        *,
        status: SyncStatus,
        finished_at: datetime,
        counters: SyncCounters,
        fatal_error: str | None,
    ) -> None:
        run = self.session.get_one(SyncRunModel, run_id)
        run.status = status.value
        run.finished_at = finished_at
        run.fetched_count = counters.fetched
        run.inserted_count = counters.inserted
        run.updated_count = counters.updated
        run.unchanged_count = counters.unchanged
        run.failed_count = counters.failed
        run.fatal_error = fatal_error

    def latest_success_upper_watermark(self) -> datetime | None:
        return self.session.scalar(
            select(SyncRunModel.upper_watermark)
            .where(SyncRunModel.status == SyncStatus.SUCCESS.value)
            .where(SyncRunModel.upper_watermark.is_not(None))
            .order_by(SyncRunModel.finished_at.desc())
            .limit(1)
        )


class SqlSyncLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(
        self,
        *,
        sync_run_id: int,
        entity_type: str,
        odoo_id: int | None,
        attempted_operation: str,
        error_type: str,
        error_message: str,
    ) -> None:
        self.session.add(
            SyncLogModel(
                sync_run_id=sync_run_id,
                entity_type=entity_type,
                odoo_id=odoo_id,
                attempted_operation=attempted_operation,
                error_type=error_type,
                error_message=error_message,
            )
        )
