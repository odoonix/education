from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class SaleOrder(BaseModel):
    __tablename__ = "sale_orders"

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    order_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id"),
    )

    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    state: Mapped[str] = mapped_column(
        String(50),
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
    )

    contact = relationship(
        "Contact",
        back_populates="sale_orders",
    )

    lines = relationship(
        "SaleOrderLine",
        back_populates="sale_order",
        cascade="all, delete-orphan",
    )
