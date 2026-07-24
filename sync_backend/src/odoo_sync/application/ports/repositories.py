from __future__ import annotations

from datetime import datetime
from typing import Protocol

from odoo_sync.domain.models import Contact, Product, SaleOrder, SaleOrderLine
from odoo_sync.domain.sync import SyncCounters, SyncStatus, SyncType, UpsertResult


class ContactRepository(Protocol):
    def find_id_by_odoo_id(self, odoo_id: int) -> int | None: ...
    def upsert(self, contact: Contact) -> UpsertResult: ...


class ProductRepository(Protocol):
    def find_id_by_odoo_id(self, odoo_id: int) -> int | None: ...
    def upsert(self, product: Product) -> UpsertResult: ...


class SaleOrderRepository(Protocol):
    def find_id_by_odoo_id(self, odoo_id: int) -> int | None: ...
    def upsert(self, order: SaleOrder, *, customer_id: int) -> UpsertResult: ...


class SaleOrderLineRepository(Protocol):
    def upsert(
        self, line: SaleOrderLine, *, sale_order_id: int, product_id: int
    ) -> UpsertResult: ...


class SyncRunRepository(Protocol):
    def start(
        self,
        *,
        sync_type: SyncType,
        lower_watermark: datetime | None,
        upper_watermark: datetime | None,
        started_at: datetime,
    ) -> int: ...

    def finish(
        self,
        run_id: int,
        *,
        status: SyncStatus,
        finished_at: datetime,
        counters: SyncCounters,
        fatal_error: str | None,
    ) -> None: ...

    def latest_success_upper_watermark(self) -> datetime | None: ...


class SyncLogRepository(Protocol):
    def add(
        self,
        *,
        sync_run_id: int,
        entity_type: str,
        odoo_id: int | None,
        attempted_operation: str,
        error_type: str,
        error_message: str,
    ) -> None: ...
