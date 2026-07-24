from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from odoo_sync.infrastructure.database.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OdooSourceMixin(TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    odoo_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    odoo_write_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ContactModel(OdooSourceMixin, Base):
    __tablename__ = "contacts"

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(64))
    mobile: Mapped[str | None] = mapped_column(String(64))
    sale_orders: Mapped[list[SaleOrderModel]] = relationship(back_populates="customer")


class ProductModel(OdooSourceMixin, Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255))
    internal_reference: Mapped[str | None] = mapped_column(String(128))
    sale_price: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    product_type: Mapped[str] = mapped_column(String(64))
    sale_order_lines: Mapped[list[SaleOrderLineModel]] = relationship(back_populates="product")


class SaleOrderModel(OdooSourceMixin, Base):
    __tablename__ = "sale_orders"

    order_number: Mapped[str] = mapped_column(String(128))
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id", ondelete="RESTRICT"), index=True
    )
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    state: Mapped[str] = mapped_column(String(64))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    customer: Mapped[ContactModel] = relationship(back_populates="sale_orders")
    lines: Mapped[list[SaleOrderLineModel]] = relationship(
        back_populates="sale_order", cascade="all, delete-orphan", passive_deletes=True
    )


class SaleOrderLineModel(OdooSourceMixin, Base):
    __tablename__ = "sale_order_lines"

    sale_order_id: Mapped[int] = mapped_column(
        ForeignKey("sale_orders.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    sale_order: Mapped[SaleOrderModel] = relationship(back_populates="lines")
    product: Mapped[ProductModel] = relationship(back_populates="sale_order_lines")


class SyncRunModel(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sync_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    inserted_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, default=0)
    unchanged_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    lower_watermark: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    upper_watermark: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fatal_error: Mapped[str | None] = mapped_column(Text())
    logs: Mapped[list[SyncLogModel]] = relationship(
        back_populates="sync_run", cascade="all, delete-orphan", passive_deletes=True
    )


class SyncLogModel(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sync_run_id: Mapped[int] = mapped_column(
        ForeignKey("sync_runs.id", ondelete="CASCADE"), index=True
    )
    entity_type: Mapped[str] = mapped_column(String(64))
    odoo_id: Mapped[int | None] = mapped_column(Integer)
    attempted_operation: Mapped[str] = mapped_column(String(64))
    error_type: Mapped[str] = mapped_column(String(128))
    error_message: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sync_run: Mapped[SyncRunModel] = relationship(back_populates="logs")
