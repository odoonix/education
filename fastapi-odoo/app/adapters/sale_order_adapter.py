from app.adapters.odoo_client import OdooClient
from app.schemas.odoo import get_odoo_id
from app.schemas.sale_order import (
    OdooSaleOrder,
    OdooSaleOrderLine,
)


class SaleOrderAdapter:
    def __init__(self, client: OdooClient) -> None:
        self._client = client

    def fetch_orders(self) -> list[OdooSaleOrder]:
        records = self._client.search_read(
            model="sale.order",
            fields=[
                "id",
                "name",
                "partner_id",
                "date_order",
                "state",
                "amount_total",
                "order_line",
            ],
        )

        return [
            OdooSaleOrder.model_validate(record)
            for record in records
        ]

    def fetch_order_lines(
        self,
    ) -> list[OdooSaleOrderLine]:
        records = self._client.search_read(
            model="sale.order.line",
            fields=[
                "id",
                "order_id",
                "product_id",
                "product_uom_qty",
                "price_unit",
                "price_subtotal",
            ],
        )

        return [
            OdooSaleOrderLine.model_validate(record)
            for record in records
        ]