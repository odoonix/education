from typing import Any

from src.domain.models import SaleOrderLine
from src.mappers.base_mapper import BaseMapper, extract_many2one_id


class SaleOrderLineMapper(BaseMapper[SaleOrderLine]):
    def to_domain(self, raw: dict[str, Any]) -> SaleOrderLine:
        return SaleOrderLine(
            odoo_id=raw["id"],
            order_odoo_id=extract_many2one_id(raw.get("order_id")),
            product_odoo_id=extract_many2one_id(raw.get("product_id")),
            quantity=raw.get("product_uom_qty") or 0.0,
            unit_price=raw.get("price_unit") or 0.0,
            subtotal=raw.get("price_subtotal") or 0.0,
        )
