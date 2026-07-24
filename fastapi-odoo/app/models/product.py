from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.sale_order_line import SaleOrderLine


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("odoo_id", name="uq_products_odoo_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    internal_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    sale_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    product_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

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

    sale_order_lines: Mapped[list["SaleOrderLine"]] = relationship(
        back_populates="product",
    )