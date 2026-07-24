from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from odoo_sync.domain.exceptions import MappingError
from odoo_sync.domain.models import Contact, Product, SaleOrder, SaleOrderLine


def optional_text(value: object) -> str | None:
    return None if value is False or value is None else str(value)


def required_text(record: dict[str, Any], field: str) -> str:
    value = record.get(field)
    if value is False or value is None or str(value) == "":
        raise MappingError(f"missing required field {field}")
    return str(value)


def decimal_value(record: dict[str, Any], field: str) -> Decimal:
    try:
        return Decimal(str(record[field]))
    except Exception as exc:
        raise MappingError(f"invalid decimal field {field}") from exc


def utc_datetime(value: object, *, required: bool = False) -> datetime | None:
    if value is False or value is None:
        if required:
            raise MappingError("missing required datetime")
        return None
    if not isinstance(value, str):
        raise MappingError("invalid datetime type")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise MappingError("invalid datetime value") from exc
    return parsed.replace(tzinfo=UTC)


def many2one_id(record: dict[str, Any], field: str) -> int:
    value = record.get(field)
    if not isinstance(value, list | tuple) or not value or not isinstance(value[0], int):
        raise MappingError(f"invalid many2one field {field}")
    return int(value[0])


def raw_id(record: dict[str, Any]) -> int | None:
    value = record.get("id")
    return value if isinstance(value, int) else None


def map_contact(record: dict[str, Any]) -> Contact:
    return Contact(
        odoo_id=int(record["id"]),
        name=required_text(record, "name"),
        email=optional_text(record.get("email")),
        phone=optional_text(record.get("phone")),
        mobile=optional_text(record.get("mobile")),
        odoo_write_date=utc_datetime(record.get("write_date")),
    )


def map_product(record: dict[str, Any]) -> Product:
    return Product(
        odoo_id=int(record["id"]),
        name=required_text(record, "name"),
        internal_reference=optional_text(record.get("default_code")),
        sale_price=decimal_value(record, "list_price"),
        product_type=required_text(record, "detailed_type"),
        odoo_write_date=utc_datetime(record.get("write_date")),
    )


def map_sale_order(record: dict[str, Any]) -> SaleOrder:
    order_date = utc_datetime(record.get("date_order"), required=True)
    assert order_date is not None
    return SaleOrder(
        odoo_id=int(record["id"]),
        order_number=required_text(record, "name"),
        customer_odoo_id=many2one_id(record, "partner_id"),
        order_date=order_date,
        state=required_text(record, "state"),
        total_amount=decimal_value(record, "amount_total"),
        odoo_write_date=utc_datetime(record.get("write_date")),
    )


def map_sale_order_line(record: dict[str, Any]) -> SaleOrderLine:
    return SaleOrderLine(
        odoo_id=int(record["id"]),
        sale_order_odoo_id=many2one_id(record, "order_id"),
        product_odoo_id=many2one_id(record, "product_id"),
        quantity=decimal_value(record, "product_uom_qty"),
        unit_price=decimal_value(record, "price_unit"),
        subtotal=decimal_value(record, "price_subtotal"),
        odoo_write_date=utc_datetime(record.get("write_date")),
    )
