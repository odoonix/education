from repositories.product_repository import ProductRepository
from core.entities import ProductEntity


def test_upsert_creates_new_product(db_session):
    repo = ProductRepository(db_session)
    entity = ProductEntity(odoo_id=1, name="Widget", default_code="W-1", list_price=10.0, product_type="consu")

    product_id, created = repo.upsert(entity)

    assert created is True
    assert product_id is not None


def test_upsert_is_idempotent(db_session):
    repo = ProductRepository(db_session)
    entity = ProductEntity(odoo_id=1, name="Original", default_code="W-1", list_price=10.0, product_type="consu")

    id1, created1 = repo.upsert(entity)
    entity.list_price = 15.0
    id2, created2 = repo.upsert(entity)

    assert id1 == id2
    assert created1 is True
    assert created2 is False

    stored = repo.get_by_odoo_id(1)
    assert stored.list_price == 15.0