from datetime import datetime
from decimal import Decimal

from app.domain.entities.sale_order import SaleOrder


def test_create_sale_order():
    order = SaleOrder(
        odoo_id=100,
        order_number="SO0001",
        customer_id=1,
        order_date=datetime(2026, 7, 23),
        state="sale",
        total_amount=Decimal("2000.00"),
    )

    assert order.odoo_id == 100
    assert order.order_number == "SO0001"
    assert order.customer_id == 1
    assert order.state == "sale"
    assert order.total_amount == Decimal("2000.00")
    