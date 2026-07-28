from typing import Any

from src.domain.models import Product
from src.mappers.base_mapper import BaseMapper


class ProductMapper(BaseMapper[Product]):
    def to_domain(self, raw: dict[str, Any]) -> Product:
        return Product(
            odoo_id=raw["id"],
            name=raw["name"],
            internal_reference=raw.get("default_code") or None,
            sale_price=raw.get("list_price") or 0.0,
            product_type=raw.get("type") or None,
        )
