from repositories.contact_repository import ContactRepository
from core.entities import ContactEntity


def test_upsert_creates_new_contact(db_session):
    repo = ContactRepository(db_session)
    entity = ContactEntity(odoo_id=1, name="Test User", email="t@test.com", phone=None, mobile=None)

    contact_id, created = repo.upsert(entity)

    assert created is True
    assert contact_id is not None


def test_upsert_is_idempotent(db_session):
    repo = ContactRepository(db_session)
    entity = ContactEntity(odoo_id=1, name="Original Name", email="t@test.com", phone=None, mobile=None)

    id1, created1 = repo.upsert(entity)
    entity.name = "Updated Name"
    id2, created2 = repo.upsert(entity)

    assert id1 == id2                # همون رکورد، نه رکورد جدید
    assert created1 is True
    assert created2 is False

    stored = repo.get_by_odoo_id(1)
    assert stored.name == "Updated Name"   # مطمئن می‌شیم Update واقعاً اعمال شده


def test_get_by_odoo_id_returns_none_when_missing(db_session):
    repo = ContactRepository(db_session)
    assert repo.get_by_odoo_id(999) is None