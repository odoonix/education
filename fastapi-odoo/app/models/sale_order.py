from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.sale_order_line import SaleOrderLine


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    __table_args__ = (
        UniqueConstraint("odoo_id", name="uq_sale_orders_odoo_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    odoo_id: Mapped[int] = mapped_column(nullable=False)

    order_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id"),
        nullable=False,
    )

    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    contact: Mapped["Contact"] = relationship(
        back_populates="sale_orders",
    )

    lines: Mapped[list["SaleOrderLine"]] = relationship(
        back_populates="sale_order",
        cascade="all, delete-orphan",
    )