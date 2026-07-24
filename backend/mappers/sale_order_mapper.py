from datetime import datetime

from core.entities import SaleOrderEntity
from mappers.utils import extract_id


def map_sale_order(raw: dict) -> SaleOrderEntity:
    return SaleOrderEntity(
        odoo_id=raw["id"],
        name=raw["name"],
        contact_odoo_id=extract_id(raw["partner_id"]),
        date_order=datetime.strptime(raw["date_order"], "%Y-%m-%d %H:%M:%S"),
        state=raw["state"],
        amount_total=raw["amount_total"],
    )