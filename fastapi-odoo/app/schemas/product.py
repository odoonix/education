from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas.odoo import get_odoo_id


class OdooProductVariant(BaseModel):
    odoo_id: int = Field(alias="id")
    product_template_id: int = Field(alias="product_tmpl_id")
    name: str
    internal_reference: str | None = Field(
        default=None,
        alias="default_code",
    )
    sale_price: Decimal = Field(alias="lst_price")

    @field_validator("product_template_id", mode="before")
    @classmethod
    def normalize_product_template_id(
        cls,
        value: list | int,
    ) -> int:
        return get_odoo_id(value)

    model_config = {
        "populate_by_name": True,
    }


class OdooProductTemplate(BaseModel):
    odoo_id: int = Field(alias="id")
    sale_price: Decimal = Field(alias="list_price")
    product_type: str = Field(alias="type")

    model_config = {
        "populate_by_name": True,
    }


class OdooProduct(BaseModel):
    odoo_id: int
    name: str
    internal_reference: str | None
    sale_price: Decimal
    product_type: str