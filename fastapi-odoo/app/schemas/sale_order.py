from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas.odoo import get_odoo_id


class OdooSaleOrder(BaseModel):
    odoo_id: int = Field(alias="id")
    order_number: str = Field(alias="name")
    partner_id: int
    order_date: datetime = Field(alias="date_order")
    state: str
    total_amount: Decimal = Field(alias="amount_total")
    order_line: list[int]

    @field_validator("partner_id", mode="before")
    @classmethod
    def normalize_partner_id(
        cls,
        value: list | int,
    ) -> int:
        return get_odoo_id(value)

    model_config = {
        "populate_by_name": True,
    }


class OdooSaleOrderLine(BaseModel):
    odoo_id: int = Field(alias="id")
    order_id: int
    product_id: int
    quantity: Decimal = Field(alias="product_uom_qty")
    unit_price: Decimal = Field(alias="price_unit")
    subtotal: Decimal = Field(alias="price_subtotal")

    @field_validator(
        "order_id",
        "product_id",
        mode="before",
    )
    @classmethod
    def normalize_relation_ids(
        cls,
        value: list | int,
    ) -> int:
        return get_odoo_id(value)

    model_config = {
        "populate_by_name": True,
    }