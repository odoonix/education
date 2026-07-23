from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.sale_order_line import SaleOrderLineModel


class ProductModel(Base):
    __tablename__ = "products"

    odoo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255))
    internal_reference: Mapped[str | None] = mapped_column(String(64))
    sale_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    product_type: Mapped[str | None] = mapped_column(String(32))

    sale_order_lines: Mapped[list["SaleOrderLineModel"]] = relationship(
        back_populates="product",
    )
