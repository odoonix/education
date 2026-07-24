from decimal import Decimal

from backend.domain.entities import Contact, Product, SaleOrder, SaleOrderLine
from backend.repositories.repositories import (
    ContactRepository,
    ProductRepository,
    SaleOrderRepository,
)


def test_contact_upsert_creates_new_record(session):
    repo = ContactRepository(session)
    contact = Contact(odoo_id=1, name="Ali Rezaei", email="ali@example.com", phone="123", mobile="456")

    model, created = repo.upsert(contact)
    session.commit()

    assert created is True
    assert model.odoo_id == 1
    assert model.name == "Ali Rezaei"


def test_contact_upsert_updates_existing_record_without_duplicating(session):
    repo = ContactRepository(session)
    original = Contact(odoo_id=1, name="Ali Rezaei", email="ali@example.com", phone="123", mobile="456")
    repo.upsert(original)
    session.commit()

    changed = Contact(odoo_id=1, name="Ali R. Updated", email="ali@example.com", phone="999", mobile="456")
    model, created = repo.upsert(changed)
    session.commit()

    assert created is False
    assert model.name == "Ali R. Updated"
    assert model.phone == "999"

    all_contacts = session.query(type(model)).filter_by(odoo_id=1).all()
    assert len(all_contacts) == 1


def test_product_upsert_is_idempotent(session):
    repo = ProductRepository(session)
    product = Product(odoo_id=10, name="Mouse", internal_reference="PRD-001", sale_price=Decimal("15.50"), product_type="consu")

    repo.upsert(product)
    session.commit()
    repo.upsert(product)
    session.commit()

    all_products = session.query(type(repo.upsert(product)[0])).filter_by(odoo_id=10).all()
    assert len(all_products) == 1


def test_sale_order_upsert_creates_lines(session):
    contact_repo = ContactRepository(session)
    product_repo = ProductRepository(session)
    order_repo = SaleOrderRepository(session)

    customer, _ = contact_repo.upsert(
        Contact(odoo_id=1, name="Ali", email="ali@example.com", phone=None, mobile=None)
    )
    product, _ = product_repo.upsert(
        Product(odoo_id=10, name="Mouse", internal_reference="PRD-001", sale_price=Decimal("15.50"), product_type="consu")
    )
    session.commit()

    line = SaleOrderLine(odoo_id=100, product_odoo_id=10, quantity=Decimal("2"), unit_price=Decimal("15.50"), subtotal=Decimal("31.00"))
    order = SaleOrder(
        odoo_id=1000,
        order_number="S00001",
        customer_odoo_id=1,
        order_date=customer.created_at,
        state="sale",
        total_amount=Decimal("31.00"),
        lines=[line],
    )

    model, created = order_repo.upsert(order, customer, {10: product})
    session.commit()

    assert created is True
    assert len(model.lines) == 1
    assert model.lines[0].odoo_id == 100


def test_sale_order_upsert_updates_lines_without_duplicating(session):
    contact_repo = ContactRepository(session)
    product_repo = ProductRepository(session)
    order_repo = SaleOrderRepository(session)

    customer, _ = contact_repo.upsert(
        Contact(odoo_id=1, name="Ali", email="ali@example.com", phone=None, mobile=None)
    )
    product, _ = product_repo.upsert(
        Product(odoo_id=10, name="Mouse", internal_reference="PRD-001", sale_price=Decimal("15.50"), product_type="consu")
    )
    session.commit()

    line = SaleOrderLine(odoo_id=100, product_odoo_id=10, quantity=Decimal("2"), unit_price=Decimal("15.50"), subtotal=Decimal("31.00"))
    order = SaleOrder(
        odoo_id=1000, order_number="S00001", customer_odoo_id=1,
        order_date=customer.created_at, state="sale", total_amount=Decimal("31.00"), lines=[line],
    )
    order_repo.upsert(order, customer, {10: product})
    session.commit()

    updated_line = SaleOrderLine(odoo_id=100, product_odoo_id=10, quantity=Decimal("5"), unit_price=Decimal("15.50"), subtotal=Decimal("77.50"))
    order.lines = [updated_line]
    order.total_amount = Decimal("77.50")

    model, created = order_repo.upsert(order, customer, {10: product})
    session.commit()

    assert created is False
    assert len(model.lines) == 1
    assert model.lines[0].quantity == Decimal("5.00")