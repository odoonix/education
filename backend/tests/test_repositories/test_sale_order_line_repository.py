import pytest
from datetime import datetime

from repositories.contact_repository import ContactRepository
from repositories.product_repository import ProductRepository
from repositories.sale_order_repository import SaleOrderRepository
from repositories.sale_order_line_repository import SaleOrderLineRepository
from core.entities import ContactEntity, ProductEntity, SaleOrderEntity, SaleOrderLineEntity


def _setup_order(db_session):
    ContactRepository(db_session).upsert(ContactEntity(odoo_id=1, name="C", email=None, phone=None, mobile=None))
    ProductRepository(db_session).upsert(ProductEntity(odoo_id=1, name="P", default_code="P-1", list_price=10.0, product_type="consu"))
    SaleOrderRepository(db_session).upsert(
        SaleOrderEntity(odoo_id=1, name="S1", contact_odoo_id=1, date_order=datetime.now(), state="draft", amount_total=100.0)
    )


def test_upsert_resolves_both_foreign_keys(db_session):
    _setup_order(db_session)
    repo = SaleOrderLineRepository(db_session)

    line_id, created = repo.upsert(
        SaleOrderLineEntity(odoo_id=1, sale_order_odoo_id=1, product_odoo_id=1, quantity=2, unit_price=10.0, subtotal=20.0)
    )

    assert created is True
    assert line_id is not None


def test_upsert_raises_when_sale_order_missing(db_session):
    repo = SaleOrderLineRepository(db_session)

    with pytest.raises(ValueError, match="SaleOrder with odoo_id=999 not found"):
        repo.upsert(
            SaleOrderLineEntity(odoo_id=1, sale_order_odoo_id=999, product_odoo_id=1, quantity=1, unit_price=1.0, subtotal=1.0)
        )


def test_upsert_raises_when_product_missing(db_session):
    _setup_order(db_session)
    repo = SaleOrderLineRepository(db_session)

    with pytest.raises(ValueError, match="Product with odoo_id=999 not found"):
        repo.upsert(
            SaleOrderLineEntity(odoo_id=1, sale_order_odoo_id=1, product_odoo_id=999, quantity=1, unit_price=1.0, subtotal=1.0)
        )


def test_upsert_updates_existing_sale_order_line(db_session):
    _setup_order(db_session)
    repo = SaleOrderLineRepository(db_session)

    entity = SaleOrderLineEntity(odoo_id=1, sale_order_odoo_id=1, product_odoo_id=1, quantity=2, unit_price=10.0, subtotal=20.0)
    id1, created1 = repo.upsert(entity)

    entity.quantity = 5
    entity.subtotal = 50.0
    id2, created2 = repo.upsert(entity)

    assert id1 == id2
    assert created1 is True
    assert created2 is False

    stored = repo.get_by_odoo_id(1)
    assert float(stored.quantity) == 5