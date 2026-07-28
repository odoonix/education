from typing import Any

from src.db.models import Product as ProductORM
from src.domain.models import Product as ProductDomain
from src.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[ProductORM, ProductDomain]):
    model_class = ProductORM

    def _to_orm_kwargs(self, domain: ProductDomain, **extra: Any) -> dict[str, Any]:
        return {
            "odoo_id": domain.odoo_id,
            "name": domain.name,
            "internal_reference": domain.internal_reference,
            "sale_price": domain.sale_price,
            "product_type": domain.product_type,
        }
