"""
Tests for the Mapping layer.
All of these functions are pure - they have no IO - so no mocks or
database are needed. This simplicity is exactly the design goal of this layer.
"""
from datetime import date
from decimal import Decimal

from app.mapping.mappers import (
    extract_order_odoo_id,
    extract_partner_odoo_id,
    extract_product_odoo_id,
    map_contact,
    map_product,
    map_sale_order,
    map_sale_order_line,
)


class TestMapContact:
    def test_maps_all_fields(self):
        raw = {"id": 1, "name": "Ali", "email": "ali@x.com", "phone": "111", "mobile": "222"}
        result = map_contact(raw)
        assert result == {
            "name": "Ali",
            "email": "ali@x.com",
            "phone": "111",
            "mobile": "222",
        }

    def test_missing_optional_fields_become_none(self):
        raw = {"id": 1, "name": "Ali"}
        result = map_contact(raw)
        assert result["email"] is None
        assert result["phone"] is None
        assert result["mobile"] is None

    def test_odoo_false_becomes_none(self):
        raw = {"id": 1, "name": "Ali", "email": False, "phone": False, "mobile": False}
        result = map_contact(raw)
        assert result["email"] is None
        assert result["phone"] is None
        assert result["mobile"] is None

    def test_missing_name_becomes_empty_string_not_none(self):
        raw = {"id": 1}
        result = map_contact(raw)
        assert result["name"] == ""


class TestMapProduct:
    def test_maps_all_fields_with_detailed_type(self):
        raw = {
            "id": 7,
            "name": "Laptop",
            "default_code": "SKU-A",
            "list_price": 1000.5,
            "type": "consu",
            "detailed_type": "product",
        }
        result = map_product(raw)
        assert result["name"] == "Laptop"
        assert result["internal_reference"] == "SKU-A"
        assert result["sale_price"] == Decimal("1000.5")
        assert result["product_type"] == "product"

    def test_falls_back_to_type_when_no_detailed_type(self):
        raw = {"id": 7, "name": "Laptop", "type": "consu"}
        result = map_product(raw)
        assert result["product_type"] == "consu"

    def test_invalid_price_becomes_none(self):
        raw = {"id": 7, "name": "Laptop", "list_price": "not-a-number"}
        result = map_product(raw)
        assert result["sale_price"] is None

    def test_missing_price_becomes_none(self):
        raw = {"id": 7, "name": "Laptop", "list_price": False}
        result = map_product(raw)
        assert result["sale_price"] is None


class TestMapSaleOrder:
    def test_maps_all_fields(self):
        raw = {
            "id": 100,
            "name": "S00001",
            "partner_id": [3, "Ali Rezaei"],
            "date_order": "2026-07-20 10:30:00",
            "state": "sale",
            "amount_total": 199.99,
        }
        result = map_sale_order(raw, customer_internal_id=1)
        assert result == {
            "order_number": "S00001",
            "customer_id": 1,
            "order_date": date(2026, 7, 20),
            "state": "sale",
            "total_amount": Decimal("199.99"),
        }

    def test_date_only_string_also_works(self):
        raw = {"id": 100, "date_order": "2026-01-05"}
        result = map_sale_order(raw, customer_internal_id=None)
        assert result["order_date"] == date(2026, 1, 5)

    def test_missing_date_becomes_none(self):
        raw = {"id": 100, "date_order": False}
        result = map_sale_order(raw, customer_internal_id=None)
        assert result["order_date"] is None

    def test_invalid_date_becomes_none(self):
        raw = {"id": 100, "date_order": "not-a-date"}
        result = map_sale_order(raw, customer_internal_id=None)
        assert result["order_date"] is None

    def test_customer_internal_id_none_is_allowed(self):
        raw = {"id": 100, "name": "S00001"}
        result = map_sale_order(raw, customer_internal_id=None)
        assert result["customer_id"] is None


class TestMapSaleOrderLine:
    def test_maps_all_fields(self):
        raw = {
            "id": 1000,
            "order_id": [100, "S00001"],
            "product_id": [7, "Laptop"],
            "product_uom_qty": 2,
            "price_unit": 500,
            "price_subtotal": 1000,
        }
        result = map_sale_order_line(raw, sale_order_internal_id=1, product_internal_id=2)
        assert result == {
            "sale_order_id": 1,
            "product_id": 2,
            "quantity": Decimal("2"),
            "unit_price": Decimal("500"),
            "subtotal": Decimal("1000"),
        }

    def test_product_internal_id_can_be_none(self):
        raw = {"id": 1000, "product_uom_qty": 1, "price_unit": 1, "price_subtotal": 1}
        result = map_sale_order_line(raw, sale_order_internal_id=1, product_internal_id=None)
        assert result["product_id"] is None


class TestRelationalIdExtractors:
    def test_extract_partner_odoo_id_from_many2one_pair(self):
        raw = {"partner_id": [3, "Ali Rezaei"]}
        assert extract_partner_odoo_id(raw) == 3

    def test_extract_partner_odoo_id_when_false(self):
        raw = {"partner_id": None}
        assert extract_partner_odoo_id(raw) is None

    def test_extract_partner_odoo_id_missing_key(self):
        assert extract_partner_odoo_id({}) is None

    def test_extract_product_odoo_id(self):
        raw = {"product_id": [7, "[SKU-A] Laptop"]}
        assert extract_product_odoo_id(raw) == 7

    def test_extract_order_odoo_id(self):
        raw = {"order_id": [100, "S00001"]}
        assert extract_order_odoo_id(raw) == 100

    def test_extract_handles_plain_int_too(self):
        raw = {"partner_id": 5}
        assert extract_partner_odoo_id(raw) == 5
