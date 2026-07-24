from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from datetime import datetime
from typing import Any, TypeVar

from odoo_sync.domain.models import Contact, Product, SaleOrder, SaleOrderLine
from odoo_sync.domain.read_outcome import ReadRecord
from odoo_sync.infrastructure.odoo.client import OdooClient
from odoo_sync.infrastructure.odoo.mappers import (
    map_contact,
    map_product,
    map_sale_order,
    map_sale_order_line,
    raw_id,
)

T = TypeVar("T")


class OdooAdapter:
    def __init__(self, client: OdooClient) -> None:
        self.client = client

    def get_upper_watermark(self) -> datetime:
        return self.client.now()

    def iter_contacts(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[Contact]]:
        yield from self._iter_records(
            "res.partner",
            ["id", "name", "email", "phone", "mobile", "write_date"],
            map_contact,
            page_size,
            lower,
            upper,
        )

    def iter_products(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[Product]]:
        yield from self._iter_records(
            "product.product",
            ["id", "name", "default_code", "list_price", "detailed_type", "write_date"],
            map_product,
            page_size,
            lower,
            upper,
        )

    def iter_sale_orders(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[SaleOrder]]:
        yield from self._iter_records(
            "sale.order",
            ["id", "name", "partner_id", "date_order", "state", "amount_total", "write_date"],
            map_sale_order,
            page_size,
            lower,
            upper,
        )

    def iter_sale_order_lines(
        self, *, page_size: int, lower: datetime | None, upper: datetime | None
    ) -> Iterator[ReadRecord[SaleOrderLine]]:
        yield from self._iter_records(
            "sale.order.line",
            [
                "id",
                "order_id",
                "product_id",
                "product_uom_qty",
                "price_unit",
                "price_subtotal",
                "write_date",
            ],
            map_sale_order_line,
            page_size,
            lower,
            upper,
        )

    def _iter_records(
        self,
        model: str,
        fields: Sequence[str],
        mapper: Callable[[dict[str, Any]], T],
        page_size: int,
        lower: datetime | None,
        upper: datetime | None,
    ) -> Iterator[ReadRecord[T]]:
        last_id = 0
        while True:
            domain: list[Any] = [["id", ">", last_id]]
            if lower is not None:
                domain.append(["write_date", ">", lower.strftime("%Y-%m-%d %H:%M:%S")])
            if upper is not None:
                domain.append(["write_date", "<=", upper.strftime("%Y-%m-%d %H:%M:%S")])
            page = self.client.search_read(model, domain, fields, limit=page_size)
            if not page:
                return
            for record in page:
                last_id = max(last_id, raw_id(record) or last_id)
                try:
                    yield ReadRecord(raw_id=raw_id(record), value=mapper(record))
                except Exception as exc:
                    yield ReadRecord(raw_id=raw_id(record), value=None, error=exc)
            if len(page) < page_size:
                return
