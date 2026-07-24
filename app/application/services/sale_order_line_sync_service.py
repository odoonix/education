from decimal import Decimal

from app.infrastructure.odoo.client import OdooClient
from app.application.dto.sale_order_line_dto import SaleOrderLineDTO
from app.application.mappers.sale_order_line_mapper import SaleOrderLineMapper


class SaleOrderLineSyncService:

    def __init__(
        self,
        odoo_client: OdooClient,
    ):
        self.odoo_client = odoo_client

    def sync(self):

        sale_order_lines = self.odoo_client.get_sale_order_lines()

        entities = []

        for sale_order_line in sale_order_lines:

            if not sale_order_line.get("product_id"):
                continue

            dto = SaleOrderLineDTO(
                odoo_id=sale_order_line["id"],
                sale_order_id=sale_order_line["order_id"][0],
                product_id=sale_order_line["product_id"][0],
                quantity=sale_order_line["product_uom_qty"],
                unit_price=Decimal(
                    str(sale_order_line["price_unit"])
                ),
                subtotal=Decimal(
                    str(sale_order_line["price_subtotal"])
                ),
            )

            entity = SaleOrderLineMapper.to_entity(dto)

            entities.append(entity)

        return entities
