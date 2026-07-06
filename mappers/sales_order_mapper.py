from typing import Dict, Any
from models.orm_models import SaleOrder

class SaleOrderMapper:
    @staticmethod
    def to_internal(odoo_data: Dict[str, Any]) -> SaleOrder:
        # partner_id is usually a list [id, name]
        partner_id = odoo_data.get("partner_id")
        customer_id = partner_id[0] if isinstance(partner_id, list) else partner_id

        return SaleOrder(
            external_id=odoo_data.get("id"),
            order_number=odoo_data.get("name"),
            customer_id=customer_id,
            order_date=odoo_data.get("date_order"),
            state=odoo_data.get("state"),
            total_amount=odoo_data.get("amount_total"),
            amount_paid=odoo_data.get("amount_paid"),
            is_expired=odoo_data.get("is_expired", False)
        )