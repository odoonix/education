from datetime import datetime

from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255))

    default_code: Mapped[str | None] = mapped_column(
        String(100)
    )

    list_price: Mapped[float] = mapped_column(Float)

    product_type: Mapped[str] = mapped_column(
        String(30)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    sale_order_lines = relationship(
        "SaleOrderLine",
        back_populates="product",
    )