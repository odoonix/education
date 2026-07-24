from core.entities import SaleOrderLineEntity
from mappers.utils import extract_id


def map_sale_order_line(raw: dict) -> SaleOrderLineEntity:
    return SaleOrderLineEntity(
        odoo_id=raw["id"],
        sale_order_odoo_id=extract_id(raw["order_id"]),
        product_odoo_id=extract_id(raw["product_id"]),
        quantity=raw["product_uom_qty"],
        unit_price=raw["price_unit"],
        subtotal=raw["price_subtotal"],
    )