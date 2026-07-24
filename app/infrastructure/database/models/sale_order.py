from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.contact import ContactModel
    from app.infrastructure.database.models.sale_order_line import SaleOrderLineModel


class SaleOrderModel(Base):
    __tablename__ = "sale_orders"

    odoo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    order_number: Mapped[str] = mapped_column(String(64))
    customer_id: Mapped[int] = mapped_column(ForeignKey("contacts.odoo_id"))
    order_date: Mapped[datetime] = mapped_column(DateTime)
    state: Mapped[str] = mapped_column(String(32))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    customer: Mapped["ContactModel"] = relationship(
        back_populates="sale_orders",
    )
    lines: Mapped[list["SaleOrderLineModel"]] = relationship(
        back_populates="sale_order",
    )
