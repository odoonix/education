
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


def _rel_id(value: Any) -> Optional[int]:
    """take the id from a many2one field like [5, 'Ali'] and return the id only."""
    if isinstance(value, (list, tuple)) and len(value) >= 1:
        return value[0]
    if isinstance(value, int):
        return value
    return None


def _to_decimal(value: Any) -> Optional[Decimal]:
    if value in (None, False, ""):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def _to_date(value: Any) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, date):
        return value
    text = str(value)[:10]
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def map_contact(raw: dict) -> dict:
    return {
        "name": raw.get("name") or "",
        "email": raw.get("email") or None,
        "phone": raw.get("phone") or None,
        "mobile": raw.get("mobile") or None,
    }


def map_product(raw: dict) -> dict:
    product_type = raw.get("detailed_type") or raw.get("type")
    return {
        "name": raw.get("name") or "",
        "internal_reference": raw.get("default_code") or None,
        "sale_price": _to_decimal(raw.get("list_price")),
        "product_type": product_type,
    }


def map_sale_order(raw: dict, customer_internal_id: Optional[int]) -> dict:
    return {
        "order_number": raw.get("name") or None,
        "customer_id": customer_internal_id,
        "order_date": _to_date(raw.get("date_order")),
        "state": raw.get("state") or None,
        "total_amount": _to_decimal(raw.get("amount_total")),
    }


def map_sale_order_line(
    raw: dict, sale_order_internal_id: int, product_internal_id: Optional[int]
) -> dict:
    return {
        "sale_order_id": sale_order_internal_id,
        "product_id": product_internal_id,
        "quantity": _to_decimal(raw.get("product_uom_qty")),
        "unit_price": _to_decimal(raw.get("price_unit")),
        "subtotal": _to_decimal(raw.get("price_subtotal")),
    }


def extract_partner_odoo_id(raw_sale_order: dict) -> Optional[int]:
    return _rel_id(raw_sale_order.get("partner_id"))


def extract_product_odoo_id(raw_sale_order_line: dict) -> Optional[int]:
    return _rel_id(raw_sale_order_line.get("product_id"))


def extract_order_odoo_id(raw_sale_order_line: dict) -> Optional[int]:
    return _rel_id(raw_sale_order_line.get("order_id"))
