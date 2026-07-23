from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ProductDTO:
    odoo_id: int
    name: str
    internal_reference: str | None
    sale_price: Decimal | None
    product_type: str | None
    