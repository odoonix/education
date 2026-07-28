from datetime import datetime
from typing import Any

from src.domain.models import SaleOrder
from src.mappers.base_mapper import BaseMapper, extract_many2one_id


class SaleOrderMapper(BaseMapper[SaleOrder]):
    def to_domain(self, raw: dict[str, Any]) -> SaleOrder:
        return SaleOrder(
            odoo_id=raw["id"],
            order_number=raw["name"],
            customer_odoo_id=extract_many2one_id(raw.get("partner_id")),
            order_date=self._parse_datetime(raw.get("date_order")),
            state=raw.get("state"),
            total_amount=raw.get("amount_total") or 0.0,
        )

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        # Odoo تاریخ رو به فرمت "YYYY-MM-DD HH:MM:SS" برمی‌گردونه
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
