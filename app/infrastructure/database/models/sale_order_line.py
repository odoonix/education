from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.product import ProductModel
    from app.infrastructure.database.models.sale_order import SaleOrderModel


class SaleOrderLineModel(Base):
    __tablename__ = "sale_order_lines"

    odoo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    sale_order_id: Mapped[int] = mapped_column(ForeignKey("sale_orders.odoo_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.odoo_id"))
    quantity: Mapped[float] = mapped_column(Float)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    sale_order: Mapped["SaleOrderModel"] = relationship(
        back_populates="lines",
    )
    product: Mapped["ProductModel"] = relationship(
        back_populates="sale_order_lines",
    )
