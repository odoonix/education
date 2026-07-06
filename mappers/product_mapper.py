from typing import Dict, Any
from models.orm_models import Product

class ProductMapper:
    @staticmethod
    def to_internal(odoo_data: Dict[str, Any]) -> Product:
        return Product(
            external_id=odoo_data.get("id"),
            name=odoo_data.get("name"),
            internal_reference=odoo_data.get("default_code") if odoo_data.get("default_code") != False else None,
            sale_price=odoo_data.get("list_price"),
            product_type=odoo_data.get("type"),
            active=odoo_data.get("active", True)
        )