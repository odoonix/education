from decimal import Decimal

from app.domain.entities.sale_order_line import SaleOrderLine


def test_create_sale_order_line():
    line = SaleOrderLine(
        odoo_id=500,
        sale_order_id=100,
        product_id=10,
        quantity=2,
        unit_price=Decimal("100.00"),
        subtotal=Decimal("200.00"),
    )

    assert line.odoo_id == 500
    assert line.sale_order_id == 100
    assert line.product_id == 10
    assert line.quantity == 2
    assert line.unit_price == Decimal("100.00")
    assert line.subtotal == Decimal("200.00")