from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Contact(BaseModel):
    __tablename__ = "contacts"

    odoo_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    mobile: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    sale_orders = relationship(
        "SaleOrder",
        back_populates="contact",
    )
