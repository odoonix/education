"""
تست‌های Repository: از fixture `session` (تعریف‌شده تو conftest.py، یک
دیتابیس SQLite خالی در حافظه) استفاده می‌کنن. مهم‌ترین چیزی که اینجا تست
می‌کنیم Idempotency هست: اجرای دوباره‌ی upsert نباید رکورد تکراری بسازه.
"""

import pytest

from src.db.models import Contact as ContactORM
from src.domain.models import Contact, Product, SaleOrder, SaleOrderLine
from src.repositories.contact_repository import ContactRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.sale_order_repository import SaleOrderRepository
from src.repositories.sale_order_line_repository import SaleOrderLineRepository


def test_contact_repository_creates_new_record(session):
    repo = ContactRepository(session)
    domain = Contact(odoo_id=1, name="Ali", email="ali@example.com")

    instance, created = repo.upsert(domain)
    session.commit()

    assert created is True
    assert instance.name == "Ali"
    assert instance.odoo_id == 1


def test_contact_repository_upsert_is_idempotent(session):
    """این مهم‌ترین تست پروژه‌ست: اجرای دوباره نباید رکورد تکراری بسازه."""
    repo = ContactRepository(session)

    # اجرای اول: باید ساخته بشه
    domain_v1 = Contact(odoo_id=1, name="Ali", email="ali@example.com")
    _, created_first = repo.upsert(domain_v1)
    session.commit()
    assert created_first is True

    # اجرای دوم با همون odoo_id ولی اسم عوض‌شده: باید آپدیت بشه نه ساخته بشه
    domain_v2 = Contact(odoo_id=1, name="Ali Rezaei (Updated)", email="ali@example.com")
    instance, created_second = repo.upsert(domain_v2)
    session.commit()

    assert created_second is False
    assert instance.name == "Ali Rezaei (Updated)"

    # مهم‌ترین چک: تو کل جدول contacts فقط باید ۱ رکورد باشه، نه ۲
    all_contacts = session.query(ContactORM).all()
    assert len(all_contacts) == 1


def test_product_repository_upsert(session):
    repo = ProductRepository(session)
    domain = Product(odoo_id=5, name="Mouse", internal_reference="PRD-001", sale_price=25.0)

    instance, created = repo.upsert(domain)
    session.commit()

    assert created is True
    assert instance.sale_price == 25.0


def test_sale_order_repository_requires_customer_id(session):
    """
    SaleOrderRepository نمی‌تونه بدون customer_id کار کنه (باید از بیرون
    پاس داده بشه). این تست مطمئن میشه این محدودیت درست اعمال شده.
    """
    repo = SaleOrderRepository(session)
    domain = SaleOrder(odoo_id=10, order_number="S00001", customer_odoo_id=1, total_amount=100.0)

    with pytest.raises(ValueError):
        repo.upsert(domain)  # customer_id رو عمداً پاس ندادیم


def test_sale_order_repository_upsert_with_customer_id(session):
    contact_repo = ContactRepository(session)
    order_repo = SaleOrderRepository(session)

    customer, _ = contact_repo.upsert(Contact(odoo_id=1, name="Ali"))
    session.flush()

    domain = SaleOrder(odoo_id=10, order_number="S00001", customer_odoo_id=1, total_amount=100.0)
    instance, created = order_repo.upsert(domain, customer_id=customer.id)
    session.commit()

    assert created is True
    assert instance.customer_id == customer.id


def test_sale_order_line_repository_requires_order_and_product_id(session):
    repo = SaleOrderLineRepository(session)
    domain = SaleOrderLine(odoo_id=100, order_odoo_id=10, product_odoo_id=5, quantity=2.0)

    with pytest.raises(ValueError):
        repo.upsert(domain)  # sale_order_id و product_id رو عمداً پاس ندادیم


def test_sale_order_line_repository_full_upsert_chain(session):
    """
    این تست کل زنجیره رو تست می‌کنه: Contact -> Sale Order -> Sale Order Line،
    دقیقاً همون ترتیبی که تو Service Layer واقعی هم رعایت میشه.
    """
    contact_repo = ContactRepository(session)
    product_repo = ProductRepository(session)
    order_repo = SaleOrderRepository(session)
    line_repo = SaleOrderLineRepository(session)

    customer, _ = contact_repo.upsert(Contact(odoo_id=1, name="Ali"))
    product, _ = product_repo.upsert(Product(odoo_id=5, name="Mouse", sale_price=25.0))
    session.flush()

    order, _ = order_repo.upsert(
        SaleOrder(odoo_id=10, order_number="S00001", customer_odoo_id=1, total_amount=50.0),
        customer_id=customer.id,
    )
    session.flush()

    line_domain = SaleOrderLine(odoo_id=100, order_odoo_id=10, product_odoo_id=5, quantity=2.0, unit_price=25.0, subtotal=50.0)
    line, created = line_repo.upsert(line_domain, sale_order_id=order.id, product_id=product.id)
    session.commit()

    assert created is True
    assert line.sale_order_id == order.id
    assert line.product_id == product.id
    assert line.subtotal == 50.0
