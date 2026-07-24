from decimal import Decimal

from backend.domain.mappers import (
    map_contact,
    map_product,
    map_sale_order,
    map_sale_order_line,
)


def test_map_contact_extracts_fields():
    raw = {"id": 1, "name": "Ali Rezaei", "email": "ali@example.com", "phone": "123", "mobile": "456"}

    contact = map_contact(raw)

    assert contact.odoo_id == 1
    assert contact.name == "Ali Rezaei"
    assert contact.email == "ali@example.com"
    assert contact.phone == "123"
    assert contact.mobile == "456"


def test_map_contact_handles_falsy_optional_fields():
    raw = {"id": 2, "name": "Sara", "email": False, "phone": False, "mobile": False}

    contact = map_contact(raw)

    assert contact.email is None
    assert contact.phone is None
    assert contact.mobile is None


def test_map_product_converts_price_to_decimal():
    raw = {"id": 10, "name": "Mouse", "default_code": "PRD-001", "list_price": 15.5, "type": "consu"}

    product = map_product(raw)

    assert product.sale_price == Decimal("15.5")
    assert isinstance(product.sale_price, Decimal)


def test_map_sale_order_unwraps_many2one_partner_tuple():
    raw = {
        "id": 1000,
        "name": "S00001",
        "partner_id": [1, "Ali Rezaei"],
        "date_order": "2026-01-15 10:30:00",
        "state": "sale",
        "amount_total": 31.0,
    }

    order = map_sale_order(raw, lines=[])

    assert order.customer_odoo_id == 1
    assert order.order_date.year == 2026
    assert order.order_date.month == 1
    assert order.order_date.day == 15


def test_map_sale_order_line_unwraps_product_tuple():
    raw = {
        "id": 100,
        "order_id": [1000, "S00001"],
        "product_id": [10, "Mouse"],
        "product_uom_qty": 2.0,
        "price_unit": 15.5,
        "price_subtotal": 31.0,
    }

    line = map_sale_order_line(raw)

    assert line.product_odoo_id == 10
    assert line.quantity == Decimal("2.0")
    assert line.subtotal == Decimal("31.0")


def test_map_sale_order_handles_missing_date():
    raw = {
        "id": 1000, "name": "S00001", "partner_id": [1, "Ali"],
        "date_order": False, "state": "draft", "amount_total": 0,
    }

    order = map_sale_order(raw, lines=[])

    assert order.order_date is not None