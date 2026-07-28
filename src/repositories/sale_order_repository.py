from typing import Any

from src.db.models import SaleOrder as SaleOrderORM
from src.domain.models import SaleOrder as SaleOrderDomain
from src.repositories.base_repository import BaseRepository


class SaleOrderRepository(BaseRepository[SaleOrderORM, SaleOrderDomain]):
    model_class = SaleOrderORM

    def _to_orm_kwargs(self, domain: SaleOrderDomain, **extra: Any) -> dict[str, Any]:
        # customer_id باید از بیرون (Service Layer) پاس داده بشه، چون این
        # Repository نمی‌دونه Contact مربوطه تو جدول contacts چه id داخلی‌ای داره.
        if "customer_id" not in extra:
            raise ValueError("SaleOrderRepository.upsert نیاز به customer_id (extra) داره.")

        return {
            "odoo_id": domain.odoo_id,
            "order_number": domain.order_number,
            "customer_id": extra["customer_id"],
            "order_date": domain.order_date,
            "state": domain.state,
            "total_amount": domain.total_amount,
        }
