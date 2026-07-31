from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from odoo_sync.application.ports.repositories import (
    ContactRepository,
    ProductRepository,
    SaleOrderLineRepository,
    SaleOrderRepository,
    SyncLogRepository,
    SyncRunRepository,
)
from odoo_sync.infrastructure.database.repositories import (
    SqlContactRepository,
    SqlProductRepository,
    SqlSaleOrderLineRepository,
    SqlSaleOrderRepository,
    SqlSyncLogRepository,
    SqlSyncRunRepository,
)


class SqlAlchemyUnitOfWork:
    contacts: ContactRepository
    products: ProductRepository
    sale_orders: SaleOrderRepository
    sale_order_lines: SaleOrderLineRepository
    sync_runs: SyncRunRepository
    sync_logs: SyncLogRepository

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def __enter__(self) -> Self:
        self.session = self.session_factory()
        self.contacts = SqlContactRepository(self.session)
        self.products = SqlProductRepository(self.session)
        self.sale_orders = SqlSaleOrderRepository(self.session)
        self.sale_order_lines = SqlSaleOrderLineRepository(self.session)
        self.sync_runs = SqlSyncRunRepository(self.session)
        self.sync_logs = SqlSyncLogRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.rollback()
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
