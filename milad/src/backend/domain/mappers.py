from datetime import datetime
from decimal import Decimal

from backend.domain.entities import Contact, Product, SaleOrder, SaleOrderLine


def map_contact(raw: dict) -> Contact:
    return Contact(
        odoo_id=raw["id"],
        name=raw["name"],
        email=raw.get("email") or None,
        phone=raw.get("phone") or None,
        mobile=raw.get("mobile") or None,
    )


def map_product(raw: dict) -> Product:
    return Product(
        odoo_id=raw["id"],
        name=raw["name"],
        internal_reference=raw.get("default_code") or None,
        sale_price=Decimal(str(raw.get("list_price", 0))),
        product_type=raw.get("type", "consu"),
    )


def map_sale_order(raw: dict, lines: list[SaleOrderLine]) -> SaleOrder:
    partner = raw.get("partner_id")
    customer_odoo_id = partner[0] if isinstance(partner, (list, tuple)) else partner

    return SaleOrder(
        odoo_id=raw["id"],
        order_number=raw["name"],
        customer_odoo_id=customer_odoo_id,
        order_date=_parse_odoo_datetime(raw.get("date_order")),
        state=raw["state"],
        total_amount=Decimal(str(raw.get("amount_total", 0))),
        lines=lines,
    )


def map_sale_order_line(raw: dict) -> SaleOrderLine:
    product = raw.get("product_id")
    product_odoo_id = product[0] if isinstance(product, (list, tuple)) else product

    return SaleOrderLine(
        odoo_id=raw["id"],
        product_odoo_id=product_odoo_id,
        quantity=Decimal(str(raw.get("product_uom_qty", 0))),
        unit_price=Decimal(str(raw.get("price_unit", 0))),
        subtotal=Decimal(str(raw.get("price_subtotal", 0))),
    )


def _parse_odoo_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.min
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")