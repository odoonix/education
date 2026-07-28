"""
تست‌های Mapper: چون Mapperها هیچ وابستگی‌ای به دیتابیس یا Odoo واقعی ندارن
(فقط dict می‌گیرن و Domain Model برمی‌گردونن)، این ساده‌ترین و سریع‌ترین
تست‌های پروژه‌ن.
"""

from datetime import datetime

from src.mappers.base_mapper import extract_many2one_id
from src.mappers.contact_mapper import ContactMapper
from src.mappers.product_mapper import ProductMapper
from src.mappers.sale_order_mapper import SaleOrderMapper
from src.mappers.sale_order_line_mapper import SaleOrderLineMapper


def test_extract_many2one_id_with_list():
    assert extract_many2one_id([15, "Ali Rezaei"]) == 15


def test_extract_many2one_id_with_false():
    # Odoo فیلد خالی رو False برمی‌گردونه، نه None
    assert extract_many2one_id(False) is None


def test_contact_mapper_converts_false_fields_to_none():
    raw = {"id": 1, "name": "Ali", "email": "ali@example.com", "phone": False, "mobile": False}
    contact = ContactMapper().to_domain(raw)

    assert contact.odoo_id == 1
    assert contact.name == "Ali"
    assert contact.email == "ali@example.com"
    assert contact.phone is None
    assert contact.mobile is None


def test_product_mapper_basic_fields():
    raw = {"id": 2, "name": "Mouse", "default_code": "PRD-001", "list_price": 25.0, "type": "consu"}
    product = ProductMapper().to_domain(raw)

    assert product.odoo_id == 2
    assert product.internal_reference == "PRD-001"
    assert product.sale_price == 25.0
    assert product.product_type == "consu"


def test_sale_order_mapper_extracts_partner_id_and_parses_date():
    raw = {
        "id": 3, "name": "S00001",
        "partner_id": [1, "Ali Rezaei"],
        "date_order": "2026-06-01 10:00:00",
        "state": "sale",
        "amount_total": 125.0,
    }
    order = SaleOrderMapper().to_domain(raw)

    assert order.customer_odoo_id == 1  # نه [1, "Ali Rezaei"]، فقط عدد
    assert order.order_date == datetime(2026, 6, 1, 10, 0, 0)
    assert order.total_amount == 125.0


def test_sale_order_line_mapper_extracts_order_and_product_ids():
    raw = {
        "id": 4, "order_id": [3, "S00001"], "product_id": [2, "Mouse"],
        "product_uom_qty": 2.0, "price_unit": 25.0, "price_subtotal": 50.0,
    }
    line = SaleOrderLineMapper().to_domain(raw)

    assert line.order_odoo_id == 3
    assert line.product_odoo_id == 2
    assert line.quantity == 2.0
    assert line.subtotal == 50.0
