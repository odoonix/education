from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


def _many2one_id(value) -> int | None:
    if not value:
        return None
    if isinstance(value, (list, tuple)):
        return int(value[0])
    return int(value)


def _many2one_name(value) -> str | None:
    if not value:
        return None
    if isinstance(value, (list, tuple)) and len(value) > 1:
        return str(value[1])
    return None


class OdooContactData(BaseModel):
    odoo_id: int
    name: str
    email: str | None = None
    phone: str | None = None
    street: str | None = None
    city: str | None = None
    country: str | None = None
    is_company: bool = False

    @classmethod
    def from_odoo(cls, record: dict) -> "OdooContactData":
        return cls(
            odoo_id=record["id"],
            name=record.get("name") or "",
            email=record.get("email") or None,
            phone=record.get("phone") or None,
            street=record.get("street") or None,
            city=record.get("city") or None,
            country=_many2one_name(record.get("country_id")),
            is_company=bool(record.get("is_company")),
        )


class OdooProductData(BaseModel):
    odoo_id: int
    name: str
    default_code: str | None = None
    list_price: Decimal = Decimal("0")
    uom_name: str | None = None
    active: bool = True

    @classmethod
    def from_odoo(cls, record: dict) -> "OdooProductData":
        return cls(
            odoo_id=record["id"],
            name=record.get("name") or "",
            default_code=record.get("default_code") or None,
            list_price=Decimal(str(record.get("list_price") or 0)),
            uom_name=_many2one_name(record.get("uom_id")),
            active=bool(record.get("active", True)),
        )


class OdooSaleOrderData(BaseModel):
    odoo_id: int
    name: str
    partner_odoo_id: int
    state: str
    amount_total: Decimal = Decimal("0")
    date_order: datetime | None = None
    line_odoo_ids: list[int] = Field(default_factory=list)

    @classmethod
    def from_odoo(cls, record: dict) -> "OdooSaleOrderData":
        date_order = record.get("date_order")
        parsed_date = None
        if date_order:
            parsed_date = datetime.fromisoformat(str(date_order).replace("Z", "+00:00"))

        return cls(
            odoo_id=record["id"],
            name=record.get("name") or "",
            partner_odoo_id=_many2one_id(record.get("partner_id")) or 0,
            state=record.get("state") or "draft",
            amount_total=Decimal(str(record.get("amount_total") or 0)),
            date_order=parsed_date,
            line_odoo_ids=list(record.get("order_line") or []),
        )


class OdooSaleOrderLineData(BaseModel):
    odoo_id: int
    order_odoo_id: int
    product_odoo_id: int | None = None
    name: str
    product_uom_qty: Decimal = Decimal("0")
    price_unit: Decimal = Decimal("0")
    price_subtotal: Decimal = Decimal("0")

    @classmethod
    def from_odoo(cls, record: dict) -> "OdooSaleOrderLineData":
        return cls(
            odoo_id=record["id"],
            order_odoo_id=_many2one_id(record.get("order_id")) or 0,
            product_odoo_id=_many2one_id(record.get("product_id")),
            name=record.get("name") or "",
            product_uom_qty=Decimal(str(record.get("product_uom_qty") or 0)),
            price_unit=Decimal(str(record.get("price_unit") or 0)),
            price_subtotal=Decimal(str(record.get("price_subtotal") or 0)),
        )
