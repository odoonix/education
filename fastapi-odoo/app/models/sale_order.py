from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    odoo_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    amount_total: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    date_order: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contact: Mapped["Contact"] = relationship("Contact", back_populates="sale_orders")
    lines: Mapped[list["SaleOrderLine"]] = relationship(
        "SaleOrderLine",
        back_populates="sale_order",
        cascade="all, delete-orphan",
    )


class SaleOrderLine(Base):
    __tablename__ = "sale_order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    odoo_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    sale_order_id: Mapped[int] = mapped_column(ForeignKey("sale_orders.id"), nullable=False, index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    product_uom_qty: Mapped[Decimal] = mapped_column(Numeric(16, 4), default=0, nullable=False)
    price_unit: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    price_subtotal: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sale_order: Mapped["SaleOrder"] = relationship("SaleOrder", back_populates="lines")
    product: Mapped["Product | None"] = relationship("Product", back_populates="sale_order_lines")
