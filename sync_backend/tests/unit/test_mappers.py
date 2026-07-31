from __future__ import annotations

from decimal import Decimal

import pytest

from odoo_sync.domain.exceptions import MappingError
from odoo_sync.infrastructure.odoo.mappers import (
    map_contact,
    map_product,
    map_sale_order,
    map_sale_order_line,
)

pytestmark = pytest.mark.unit


def test_contact_mapper_normalizes_odoo_false_and_utc_datetime() -> None:
    contact = map_contact(
        {
            "id": 10,
            "name": "A",
            "email": False,
            "phone": "1",
            "mobile": False,
            "write_date": "2026-07-24 10:00:00",
        }
    )

    assert contact.email is None
    assert contact.mobile is None
    assert contact.odoo_write_date is not None
    assert contact.odoo_write_date.tzinfo is not None


def test_product_mapper_uses_decimal_from_string() -> None:
    product = map_product(
        {
            "id": 11,
            "name": "P",
            "default_code": False,
            "list_price": 12.3,
            "detailed_type": "product",
            "write_date": False,
        }
    )

    assert product.sale_price == Decimal("12.3")
    assert product.internal_reference is None


def test_many2one_validation_for_sale_order() -> None:
    with pytest.raises(MappingError):
        map_sale_order(
            {
                "id": 12,
                "name": "SO",
                "partner_id": False,
                "date_order": "2026-07-24 10:00:00",
                "state": "draft",
                "amount_total": 1,
                "write_date": False,
            }
        )


def test_sale_order_line_mapper() -> None:
    line = map_sale_order_line(
        {
            "id": 13,
            "order_id": [20, "SO"],
            "product_id": [30, "P"],
            "product_uom_qty": 2,
            "price_unit": 5,
            "price_subtotal": 10,
            "write_date": "2026-07-24 10:00:00",
        }
    )

    assert line.sale_order_odoo_id == 20
    assert line.product_odoo_id == 30
    assert line.subtotal == Decimal("10")
