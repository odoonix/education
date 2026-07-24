from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    default_code: Mapped[str | None] = mapped_column(
        String(100),
    )

    sale_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    product_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    sale_order_lines = relationship(
        "SaleOrderLine",
        back_populates="product",
    )
