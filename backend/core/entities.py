
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContactEntity:
    odoo_id: int
    name: str
    email: str | None
    phone: str | None
    mobile: str | None


@dataclass
class ProductEntity:
    odoo_id: int
    name: str
    default_code: str | None
    list_price: float
    product_type: str


@dataclass
class SaleOrderEntity:
    odoo_id: int
    name: str
    contact_odoo_id: int
    date_order: datetime
    state: str
    amount_total: float


@dataclass
class SaleOrderLineEntity:
    odoo_id: int
    sale_order_odoo_id: int
    product_odoo_id: int
    quantity: float
    unit_price: float
    subtotal: float