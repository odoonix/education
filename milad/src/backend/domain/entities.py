from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class Contact:
    odoo_id: int
    name: str
    email: str | None
    phone: str | None
    mobile: str | None


@dataclass
class Product:
    odoo_id: int
    name: str
    internal_reference: str | None
    sale_price: Decimal
    product_type: str


@dataclass
class SaleOrderLine:
    odoo_id: int
    product_odoo_id: int
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal


@dataclass
class SaleOrder:
    odoo_id: int
    order_number: str
    customer_odoo_id: int
    order_date: datetime
    state: str
    total_amount: Decimal
    lines: list[SaleOrderLine] = field(default_factory=list)