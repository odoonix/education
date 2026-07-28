from typing import Any

from src.mappers.sale_order_line_mapper import SaleOrderLineMapper
from src.odoo_client.client import OdooClient
from src.repositories.product_repository import ProductRepository
from src.repositories.sale_order_line_repository import SaleOrderLineRepository
from src.repositories.sale_order_repository import SaleOrderRepository
from src.services.base_sync_service import BaseSyncService


class SaleOrderLineSyncService(BaseSyncService):
    operation_type = "sale_order_lines_sync"

    def __init__(self, session, odoo_client: OdooClient):
        super().__init__(session)
        self.odoo_client = odoo_client
        self.repo = SaleOrderLineRepository(session)
        self.order_repo = SaleOrderRepository(session)
        self.product_repo = ProductRepository(session)
        self.mapper = SaleOrderLineMapper()

    def fetch_records(self) -> list[dict[str, Any]]:
        since = self.get_last_successful_sync_time()
        return self.odoo_client.fetch_sale_order_lines(since=since)

    def sync_one(self, raw_record: dict[str, Any]) -> bool:
        domain = self.mapper.to_domain(raw_record)

        order = self.order_repo.get_by_odoo_id(domain.order_odoo_id)
        if order is None:
            raise ValueError(f"Sale Order با odoo_id={domain.order_odoo_id} پیدا نشد.")

        product = self.product_repo.get_by_odoo_id(domain.product_odoo_id)
        if product is None:
            raise ValueError(f"Product با odoo_id={domain.product_odoo_id} پیدا نشد.")

        _, created = self.repo.upsert(domain, sale_order_id=order.id, product_id=product.id)
        return created
