"""
Repository Tests (on real PostgreSQL test database).

The most important thing tested here is idempotency: calling upsert() with
the same odoo_id twice should not create a second record; it should update
the same record.
"""
import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models import Contact, Product, SaleOrder, SaleOrderLine
from app.repositories.contact_repository import ContactRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_order_line_repository import SaleOrderLineRepository
from app.repositories.sale_order_repository import SaleOrderRepository

from datetime import timezone, datetime
pytestmark = pytest.mark.db


class TestContactRepository:
    def test_upsert_creates_new_record(self, db_session):
        repo = ContactRepository(db_session)
        entity, created = repo.upsert(
            101, {"name": "Ali", "email": "ali@x.com", "phone": None, "mobile": None}
        )
        db_session.commit()

        assert created is True
        assert entity.odoo_id == 101
        assert db_session.query(Contact).count() == 1

    def test_upsert_twice_updates_not_duplicates(self, db_session):
        repo = ContactRepository(db_session)
        repo.upsert(101, {"name": "Ali", "email": "ali@x.com", "phone": None, "mobile": None})
        db_session.commit()

        entity2, created2 = repo.upsert(
            101, {"name": "Ali Updated", "email": "ali2@x.com", "phone": None, "mobile": None}
        )
        db_session.commit()

        assert created2 is False
        assert entity2.name == "Ali Updated"
        assert entity2.email == "ali2@x.com"
        assert db_session.query(Contact).count() == 1

    def test_get_by_odoo_id_returns_none_when_missing(self, db_session):
        repo = ContactRepository(db_session)
        assert repo.get_by_odoo_id(9999) is None

    def test_get_by_odoo_id_finds_existing(self, db_session):
        repo = ContactRepository(db_session)
        repo.upsert(101, {"name": "Ali", "email": None, "phone": None, "mobile": None})
        db_session.commit()

        found = repo.get_by_odoo_id(101)
        assert found is not None
        assert found.name == "Ali"

    def test_odoo_id_must_be_unique_at_db_level(self, db_session):
        db_session.add(Contact(odoo_id=555, name="A"))
        db_session.commit()

        db_session.add(Contact(odoo_id=555, name="B"))
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestProductRepository:
    def test_upsert_creates_and_updates(self, db_session):
        repo = ProductRepository(db_session)
        _, created1 = repo.upsert(
            7, {"name": "Laptop", "internal_reference": "SKU-A", "sale_price": 1000, "product_type": "consu"}
        )
        db_session.commit()
        entity2, created2 = repo.upsert(
            7, {"name": "Laptop Pro", "internal_reference": "SKU-A", "sale_price": 1200, "product_type": "consu"}
        )
        db_session.commit()
        assert created1 is True
        assert created2 is False
        assert entity2.name == "Laptop Pro"
        assert db_session.query(Product).count() == 1


class TestSaleOrderRepository:
    def test_upsert_creates_and_updates(self, db_session):
        contact_repo = ContactRepository(db_session)
        contact, _ = contact_repo.upsert(1, {"name": "Ali", "email": None, "phone": None, "mobile": None})
        db_session.commit()

        order_repo = SaleOrderRepository(db_session)
        entity, created = order_repo.upsert(
            100,
            {
                "order_number": "S00001",
                "customer_id": contact.id,
                "order_date": datetime.now(timezone.utc),
                "state": "draft",
                "total_amount": 0,
            },
        )
        db_session.commit()

        assert created is True
        assert entity.customer_id == contact.id
        assert db_session.query(SaleOrder).count() == 1

        entity2, created2 = order_repo.upsert(
            100,
            {
                "order_number": "S00001",
                "customer_id": contact.id,
                "order_date": datetime.now(timezone.utc),
                "state": "sale",
                "total_amount": 500,
            },
        )
        db_session.commit()

        assert created2 is False
        assert entity2.state == "sale"
        assert db_session.query(SaleOrder).count() == 1


class TestSaleOrderLineRepository:
    def test_upsert_requires_valid_sale_order_fk(self, db_session):
        line_repo = SaleOrderLineRepository(db_session)
        db_session.add(
            SaleOrderLine(odoo_id=1, sale_order_id=99999, quantity=1, unit_price=1, subtotal=1)
        )
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_upsert_creates_line_linked_to_order(self, db_session):
        order_repo = SaleOrderRepository(db_session)
        contact = Contact(odoo_id=1, name="Ali")
        db_session.add(contact)
        db_session.commit()
        product = Product(odoo_id=7, name="Laptop",internal_reference="SKU-A",sale_price=1000,product_type="consu")
        db_session.add(product)
        db_session.commit()
        order, _ = order_repo.upsert(
            100,
            {
                "order_number": "S00001",
                "customer_id": contact.id,
                "order_date": datetime.now(timezone.utc),
                "state": "draft",
                "total_amount": 0,
            },
        )
        db_session.commit()

        line_repo = SaleOrderLineRepository(db_session)
        entity, created = line_repo.upsert(
            1000,
            {
                "sale_order_id": order.id,
                "product_id": product.id,
                "quantity": 2,
                "unit_price": 100,
                "subtotal": 200,
            },
        )
        db_session.commit()

        assert created is True
        assert entity.sale_order_id == order.id
        assert db_session.query(SaleOrderLine).count() == 1
