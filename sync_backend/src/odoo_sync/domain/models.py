from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Contact:
    odoo_id: int
    name: str
    email: str | None
    phone: str | None
    mobile: str | None
    odoo_write_date: datetime | None


@dataclass(frozen=True, slots=True)
class Product:
    odoo_id: int
    name: str
    internal_reference: str | None
    sale_price: Decimal
    product_type: str
    odoo_write_date: datetime | None


@dataclass(frozen=True, slots=True)
class SaleOrder:
    odoo_id: int
    order_number: str
    customer_odoo_id: int
    order_date: datetime
    state: str
    total_amount: Decimal
    odoo_write_date: datetime | None


@dataclass(frozen=True, slots=True)
class SaleOrderLine:
    odoo_id: int
    sale_order_odoo_id: int
    product_odoo_id: int
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    odoo_write_date: datetime | None
