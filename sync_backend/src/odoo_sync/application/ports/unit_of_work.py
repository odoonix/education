from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Protocol, Self

from odoo_sync.application.ports.repositories import (
    ContactRepository,
    ProductRepository,
    SaleOrderLineRepository,
    SaleOrderRepository,
    SyncLogRepository,
    SyncRunRepository,
)


class UnitOfWork(Protocol):
    contacts: ContactRepository
    products: ProductRepository
    sale_orders: SaleOrderRepository
    sale_order_lines: SaleOrderLineRepository
    sync_runs: SyncRunRepository
    sync_logs: SyncLogRepository

    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


UnitOfWorkFactory = Callable[[], UnitOfWork]
