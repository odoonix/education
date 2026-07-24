"""
تست محدودیت‌های واقعی Postgres (نه SQLite) — Unique, Foreign Key, Cascade Delete.
از odoo_id های خیلی بزرگ (777xxx) استفاده می‌کنیم تا با داده‌های واقعی تداخل نکنه،
و هر تست خودش رکوردهایی که ساخته رو در پایان پاک می‌کنه.
"""
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from models.contacts import Contact
from models.product import Product
from models.sale_orders import SaleOrder
from models.sale_order_lines import SaleOrderLine


def test_unique_constraint_on_contact_odoo_id(pg_session):
    pg_session.add(Contact(odoo_id=777001, name="A", email=None, phone=None, mobile=None))
    pg_session.commit()

    pg_session.add(Contact(odoo_id=777001, name="B", email=None, phone=None, mobile=None))
    with pytest.raises(IntegrityError):
        pg_session.commit()
    pg_session.rollback()

    # نظافت
    pg_session.query(Contact).filter_by(odoo_id=777001).delete()
    pg_session.commit()


def test_foreign_key_constraint_enforced_at_db_level(pg_session):
    """
    این تست عمداً از Repository رد نمی‌شه (که خودش FK رو چک می‌کنه)،
    مستقیم مدل رو با contact_id غیرواقعی می‌سازه تا ببینیم خود Postgres جلوش رو می‌گیره یا نه.
    """
    bad_order = SaleOrder(
        odoo_id=777002, name="BAD-ORDER", contact_id=999_999_999,
        date_order=datetime.now(), state="draft", amount_total=10.0,
    )
    pg_session.add(bad_order)
    with pytest.raises(IntegrityError):
        pg_session.commit()
    pg_session.rollback()


def test_cascade_delete_removes_order_lines(pg_session):
    """چک می‌کنیم حذف یه Sale Order، خط‌هاش رو هم خودکار حذف می‌کنه (cascade)."""
    contact = Contact(odoo_id=777003, name="C", email=None, phone=None, mobile=None)
    product = Product(odoo_id=777003, name="P", default_code="X-777003", list_price=1.0, product_type="consu")
    pg_session.add_all([contact, product])
    pg_session.flush()

    order = SaleOrder(
        odoo_id=777003, name="O-777003", contact_id=contact.id,
        date_order=datetime.now(), state="draft", amount_total=10.0,
    )
    pg_session.add(order)
    pg_session.flush()

    line = SaleOrderLine(
        odoo_id=777003, sale_order_id=order.id, product_id=product.id,
        quantity=1, price_unit=10.0, subtotal=10.0,
    )
    pg_session.add(line)
    pg_session.commit()

    pg_session.delete(order)
    pg_session.commit()

    remaining_line = pg_session.query(SaleOrderLine).filter_by(odoo_id=777003).first()
    assert remaining_line is None   # باید خودکار پاک شده باشه

    # نظافت
    pg_session.query(Contact).filter_by(odoo_id=777003).delete()
    pg_session.query(Product).filter_by(odoo_id=777003).delete()
    pg_session.commit()