from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class SaleOrder:
    odoo_id: int
    order_number: str
    customer_id: int
    order_date: datetime
    state: str
    total_amount: Decimal