from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class SaleOrderLine(BaseModel):
    __tablename__ = "sale_order_lines"

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    sale_order_id: Mapped[int] = mapped_column(
        ForeignKey("sale_orders.id"),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
    )

    quantity: Mapped[float] = mapped_column(
        Numeric(10, 2),
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(12, 2),
    )

    sale_order = relationship(
        "SaleOrder",
        back_populates="lines",
    )

    product = relationship(
        "Product",
        back_populates="sale_order_lines",
    )
