from decimal import Decimal

from app.domain.entities.product import Product


def test_create_product():
    product = Product(
        odoo_id=10,
        name="Laptop Dell",
        internal_reference="LAP-001",
        sale_price=Decimal("1500.00"),
        product_type="product",
    )

    assert product.odoo_id == 10
    assert product.name == "Laptop Dell"
    assert product.internal_reference == "LAP-001"
    assert product.sale_price == Decimal("1500.00")
    assert product.product_type == "product"
