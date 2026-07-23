from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    odoo_id: int
    name: str
    internal_reference: str | None = None
    sale_price: Decimal | None = None
    product_type: str | None = None