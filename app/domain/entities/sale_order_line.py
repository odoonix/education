from dataclasses import dataclass
from decimal import Decimal


@dataclass
class SaleOrderLine:
    odoo_id: int
    sale_order_id: int
    product_id: int
    quantity: float
    unit_price: Decimal
    subtotal: Decimal