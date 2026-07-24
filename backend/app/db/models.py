from datetime import datetime
from sqlalchemy import (
    Integer, String, Numeric, DateTime,Text,ForeignKey
)
from sqlalchemy.orm import relationship

from .base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

class Contact(BaseModel):

    __tablename__ = "contacts"

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    mobile: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    sale_orders = relationship(
        "SaleOrder",
        back_populates="customer"
    )

class Product(BaseModel):

    __tablename__ = "products"

    odoo_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    internal_reference: Mapped[str | None] = mapped_column(
        String(100)
    )
    sale_price: Mapped[float] = mapped_column(
        Numeric(12, 2)
    )
    product_type: Mapped[str] = mapped_column(
        String(50)
    )
    order_lines = relationship(
        "SaleOrderLine",
        back_populates="product"
    )

class SaleOrder(BaseModel):

    __tablename__ = "sale_orders"

    odoo_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )
    order_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id"),
        nullable=True
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime
    )
    state: Mapped[str] = mapped_column(
        String(50)
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2)
    )
    customer = relationship(
        "Contact",
        back_populates="sale_orders"
    )
    lines = relationship(
        "SaleOrderLine",
        back_populates="sale_order",
        cascade="all, delete-orphan"
    )
    
class SaleOrderLine(BaseModel):

    __tablename__ = "sale_order_lines"

    odoo_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )
    sale_order_id: Mapped[int] = mapped_column(
        ForeignKey("sale_orders.id")
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(12,2)
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(12,2)
    )
    subtotal: Mapped[float] = mapped_column(
        Numeric(12,2)
    )
    sale_order = relationship(
        "SaleOrder",
        back_populates="lines"
    )
    product = relationship(
        "Product",
        back_populates="order_lines"
    )
    
class SyncRun(BaseModel):

    __tablename__ = "sync_runs"

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )
    received_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    created_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    updated_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    failed_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
class SyncLog(BaseModel):

    __tablename__ = "sync_logs"


    sync_run_id: Mapped[int] = mapped_column(
        ForeignKey("sync_runs.id")
    )
    level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    entity_type: Mapped[str] = mapped_column(
        String(50)
    )
    entity_odoo_id: Mapped[int] = mapped_column(
        Integer
    )
    error_message: Mapped[str] = mapped_column(
        Text
    )