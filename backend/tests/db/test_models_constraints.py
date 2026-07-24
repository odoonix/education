"""
Database Relationship Tests:
  - Cascade delete between SaleOrder and SaleOrderLine
  - Cascade delete between SyncRun and SyncLog
  - Relationship correctness (customer.orders, order.lines, ...)
"""
import pytest

from app.db.models import Contact, Product, SaleOrder, SaleOrderLine, SyncLog, SyncRun
from datetime import datetime, timezone
pytestmark = pytest.mark.db


def test_sale_order_lines_cascade_delete_with_order(db_session):
    from app.db.models import Contact
    customer = Contact(
        odoo_id=1, 
        name="Test Customer", 
        email="test@example.com"
    )
    db_session.add(customer)
    db_session.commit()
    
    product = Product(odoo_id=7, name="Laptop",internal_reference="SKU-A",sale_price=1000,product_type="consu")
    db_session.add(product)
    db_session.commit()
    order = SaleOrder(odoo_id=100, order_number="S00001", customer_id=customer.id,order_date=datetime.now(timezone.utc),state='1',total_amount=1)
    order.lines.append(SaleOrderLine(odoo_id=1000, quantity=1, unit_price=1, subtotal=1,sale_order_id=order.id,product_id=product.id))
    order.lines.append(SaleOrderLine(odoo_id=1001, quantity=2, unit_price=2, subtotal=4,sale_order_id=order.id,product_id=product.id))
    
    db_session.add(order)
    db_session.commit()

    assert db_session.query(SaleOrderLine).count() == 2

    db_session.delete(order)
    db_session.commit()

    assert db_session.query(SaleOrder).count() == 0
    assert db_session.query(SaleOrderLine).count() == 0


def test_contact_orders_relationship(db_session):
    contact = Contact(odoo_id=1, name="Ali")
    db_session.add(contact)
    db_session.commit()

    order1 = SaleOrder(odoo_id=100, order_number="S00001", customer_id=contact.id,order_date=datetime.now(timezone.utc),state='1',total_amount=1)
    order2 = SaleOrder(odoo_id=101, order_number="S00001", customer_id=contact.id,order_date=datetime.now(timezone.utc),state='1',total_amount=1)
    db_session.add_all([order1, order2])
    db_session.commit()

    db_session.refresh(contact)
    assert {o.odoo_id for o in contact.sale_orders} == {100, 101}


def test_sale_order_line_product_relationship(db_session):
    contact = Contact(odoo_id=1, name="Ali")
    db_session.add(contact)
    db_session.commit()
    product = Product(odoo_id=7, name="Laptop",internal_reference="SKU-A",sale_price=1000,product_type="consu")
    order = SaleOrder(odoo_id=100, order_number="S00001", customer_id=contact.id,order_date=datetime.now(timezone.utc),state='1',total_amount=1)
    db_session.add_all([product, order])
    db_session.commit()

    line = SaleOrderLine(odoo_id=1000, quantity=1, unit_price=1, subtotal=1,sale_order_id=order.id,product_id=product.id)
    db_session.add(line)
    db_session.commit()

    db_session.refresh(line)
    assert line.product.name == "Laptop"
    assert line.sale_order.odoo_id == 100
