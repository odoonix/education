from typing import Any

from src.db.models import SaleOrderLine as SaleOrderLineORM
from src.domain.models import SaleOrderLine as SaleOrderLineDomain
from src.repositories.base_repository import BaseRepository


class SaleOrderLineRepository(BaseRepository[SaleOrderLineORM, SaleOrderLineDomain]):
    model_class = SaleOrderLineORM

    def _to_orm_kwargs(self, domain: SaleOrderLineDomain, **extra: Any) -> dict[str, Any]:
        for required in ("sale_order_id", "product_id"):
            if required not in extra:
                raise ValueError(
                    f"SaleOrderLineRepository.upsert نیاز به {required} (extra) داره."
                )

        return {
            "odoo_id": domain.odoo_id,
            "sale_order_id": extra["sale_order_id"],
            "product_id": extra["product_id"],
            "quantity": domain.quantity,
            "unit_price": domain.unit_price,
            "subtotal": domain.subtotal,
        }
