from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Protocol

from odoo_sync.domain.models import Contact, Product, SaleOrder, SaleOrderLine
from odoo_sync.domain.read_outcome import ReadRecord


class ErpReader(Protocol):
    def get_upper_watermark(self) -> datetime: ...

    def iter_contacts(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[Contact]]: ...

    def iter_products(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[Product]]: ...

    def iter_sale_orders(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[SaleOrder]]: ...

    def iter_sale_order_lines(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[SaleOrderLine]]: ...
