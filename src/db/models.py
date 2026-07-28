"""
مدل‌های SQLAlchemy — هر کلاس اینجا معادل یک جدول تو PostgreSQL هست.

نکته‌ی مهم درباره‌ی Idempotency:
هر جدولی که از Odoo میاد (Contact, Product, SaleOrder, SaleOrderLine) یک ستون
`odoo_id` داره که UNIQUE هست. یعنی دیتابیس خودش جلوی ساخت رکورد تکراری با
همون odoo_id رو می‌گیره، و ما تو کد هم قبلش چک می‌کنیم (get_or_create).
"""

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # یک Contact می‌تونه چند تا Sale Order داشته باشه (One-to-Many)
    sale_orders = relationship("SaleOrder", back_populates="customer")

    def __repr__(self):
        return f"<Contact id={self.id} odoo_id={self.odoo_id} name={self.name!r}>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    internal_reference = Column(String(100), nullable=True, index=True)
    sale_price = Column(Float, nullable=False, default=0.0)
    product_type = Column(String(50), nullable=True)  # مثلاً consu / service

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_lines = relationship("SaleOrderLine", back_populates="product")

    def __repr__(self):
        return f"<Product id={self.id} odoo_id={self.odoo_id} name={self.name!r}>"


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    id = Column(Integer, primary_key=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    order_number = Column(String(100), nullable=False)  # مثلاً "S00001"
    customer_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    order_date = Column(DateTime, nullable=True)
    state = Column(String(50), nullable=True)  # draft / sale / done / cancel
    total_amount = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Contact", back_populates="sale_orders")
    lines = relationship(
        "SaleOrderLine", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SaleOrder id={self.id} odoo_id={self.odoo_id} number={self.order_number!r}>"


class SaleOrderLine(Base):
    __tablename__ = "sale_order_lines"

    id = Column(Integer, primary_key=True)
    odoo_id = Column(Integer, unique=True, nullable=False, index=True)
    sale_order_id = Column(Integer, ForeignKey("sale_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    unit_price = Column(Float, nullable=False, default=0.0)
    subtotal = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("SaleOrder", back_populates="lines")
    product = relationship("Product", back_populates="order_lines")

    def __repr__(self):
        return f"<SaleOrderLine id={self.id} odoo_id={self.odoo_id}>"


class SyncRun(Base):
    """
    هر بار که Sync اجرا میشه (کل فرآیند، نه هر رکورد)، یک ردیف اینجا ثبت میشه.
    این جدول جواب سوال‌های "آخرین Sync کِی بود؟ چند رکورد گرفت؟ چند خطا داشت؟" رو میده.
    """
    __tablename__ = "sync_runs"

    id = Column(Integer, primary_key=True)
    operation_type = Column(String(100), nullable=False)  # مثلاً "contacts_sync"
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="running")  # running / success / failed

    records_fetched = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    logs = relationship(
        "SyncLog", back_populates="sync_run", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SyncRun id={self.id} type={self.operation_type} status={self.status}>"


class SyncLog(Base):
    """جزئیات هر اتفاق (مخصوصاً خطاها) در طول یک SyncRun."""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True)
    sync_run_id = Column(Integer, ForeignKey("sync_runs.id"), nullable=False)
    level = Column(String(20), default="INFO")  # INFO / WARNING / ERROR
    message = Column(Text, nullable=False)
    record_reference = Column(String(255), nullable=True)  # مثلاً odoo_id رکورد مشکل‌دار
    created_at = Column(DateTime, default=datetime.utcnow)

    sync_run = relationship("SyncRun", back_populates="logs")

    def __repr__(self):
        return f"<SyncLog id={self.id} level={self.level} run_id={self.sync_run_id}>"
