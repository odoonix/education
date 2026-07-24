from sqlalchemy import (
    ForeignKey,
    Numeric,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class SaleOrderLine(Base):
    __tablename__ = "sale_order_lines"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    sale_order_id: Mapped[int] = mapped_column(
        ForeignKey("sale_orders.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[float] = mapped_column(
        Numeric(10,2)
    )

    price_unit: Mapped[float] = mapped_column(
        Numeric(12,2)
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(12,2)
    )

    sale_order = relationship(
        "SaleOrder",
        back_populates="lines",
    )

    product = relationship(
        "Product",
        back_populates="sale_order_lines",
    )