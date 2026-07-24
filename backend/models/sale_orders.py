from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Numeric,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100))

    state: Mapped[str] = mapped_column(
        String(30)
    )

    amount_total: Mapped[float] = mapped_column(
        Numeric(12,2)
    )

    date_order: Mapped[datetime]

    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id")
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
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