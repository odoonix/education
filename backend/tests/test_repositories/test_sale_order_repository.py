import pytest
from datetime import datetime

from repositories.contact_repository import ContactRepository
from repositories.sale_order_repository import SaleOrderRepository
from core.entities import ContactEntity, SaleOrderEntity


def test_upsert_resolves_contact_fk_correctly(db_session):
    ContactRepository(db_session).upsert(
        ContactEntity(odoo_id=10, name="Customer", email=None, phone=None, mobile=None)
    )

    repo = SaleOrderRepository(db_session)
    order_id, created = repo.upsert(
        SaleOrderEntity(
            odoo_id=100, name="S100", contact_odoo_id=10,
            date_order=datetime.now(), state="draft", amount_total=50.0,
        )
    )

    assert created is True
    assert order_id is not None


def test_upsert_raises_clear_error_when_contact_not_synced_yet(db_session):
    """
    اگه Contact مربوطه هنوز sync نشده باشه (یعنی sale_orders قبل از contacts
    اجرا شده باشه)، باید خطای واضح بگیریم، نه یه IntegrityError مبهم.
    """
    repo = SaleOrderRepository(db_session)

    with pytest.raises(ValueError, match="Contact with odoo_id=9999 not found"):
        repo.upsert(
            SaleOrderEntity(
                odoo_id=101, name="S101", contact_odoo_id=9999,
                date_order=datetime.now(), state="draft", amount_total=50.0,
            )
        )


def test_upsert_updates_existing_sale_order(db_session):
    from repositories.contact_repository import ContactRepository
    from core.entities import ContactEntity

    ContactRepository(db_session).upsert(
        ContactEntity(odoo_id=20, name="Customer", email=None, phone=None, mobile=None)
    )
    repo = SaleOrderRepository(db_session)

    entity = SaleOrderEntity(
        odoo_id=200, name="S200", contact_odoo_id=20,
        date_order=datetime.now(), state="draft", amount_total=100.0,
    )
    id1, created1 = repo.upsert(entity)

    entity.state = "sale"
    entity.amount_total = 150.0
    id2, created2 = repo.upsert(entity)

    assert id1 == id2
    assert created1 is True
    assert created2 is False

    stored = repo.get_by_odoo_id(200)
    assert stored.state == "sale"
    assert float(stored.amount_total) == 150.0