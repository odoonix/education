from datetime import datetime
from decimal import Decimal

from app.infrastructure.odoo.client import OdooClient
from app.application.dto.sale_order_dto import SaleOrderDTO
from app.application.mappers.sale_order_mapper import SaleOrderMapper


class SaleOrderSyncService:

    def __init__(
        self,
        odoo_client: OdooClient,
    ):
        self.odoo_client = odoo_client

    def sync(self):

        sale_orders = self.odoo_client.get_sale_orders()

        entities = []

        for sale_order in sale_orders:

            dto = SaleOrderDTO(
                odoo_id=sale_order["id"],
                order_number=sale_order["name"],
                customer_id=sale_order["partner_id"][0],
                order_date=datetime.strptime(
                    sale_order["date_order"],
                    "%Y-%m-%d %H:%M:%S",
                ),
                state=sale_order["state"],
                total_amount=Decimal(
                    str(sale_order["amount_total"])
                ),
            )

            entity = SaleOrderMapper.to_entity(dto)

            entities.append(entity)

        return entities
