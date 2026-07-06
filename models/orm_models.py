from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.session import Base

class SyncRun(Base):
    __tablename__ = "sync_runs"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="running")
    contacts_count = Column(Integer, default=0)
    products_count = Column(Integer, default=0)
    sale_orders_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    log_details = Column(Text, nullable=True)


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    city = Column(String(100))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255))
    internal_reference = Column(String(100))   # default_code
    sale_price = Column(Float)
    product_type = Column(String(50))          # type
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SaleOrder(Base):
    __tablename__ = "sale_orders"
    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False, index=True)
    order_number = Column(String(100))         # name
    customer_id = Column(Integer, ForeignKey("contacts.external_id"))
    order_date = Column(DateTime(timezone=True))
    state = Column(String(50))
    total_amount = Column(Float)
    amount_paid = Column(Float)
    is_expired = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lines = relationship("SaleOrderLine", back_populates="sale_order")


class SaleOrderLine(Base):
    __tablename__ = "sale_order_lines"
    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False, index=True)
    sale_order_id = Column(Integer, ForeignKey("sale_orders.external_id"))
    product_id = Column(Integer, ForeignKey("products.external_id"))
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float)
    subtotal = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sale_order = relationship("SaleOrder", back_populates="lines")