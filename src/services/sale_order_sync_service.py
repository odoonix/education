from typing import Any

from src.mappers.sale_order_mapper import SaleOrderMapper
from src.odoo_client.client import OdooClient
from src.repositories.contact_repository import ContactRepository
from src.repositories.sale_order_repository import SaleOrderRepository
from src.services.base_sync_service import BaseSyncService


class SaleOrderSyncService(BaseSyncService):
    operation_type = "sale_orders_sync"

    def __init__(self, session, odoo_client: OdooClient):
        super().__init__(session)
        self.odoo_client = odoo_client
        self.repo = SaleOrderRepository(session)
        self.contact_repo = ContactRepository(session)
        self.mapper = SaleOrderMapper()

    def fetch_records(self) -> list[dict[str, Any]]:
        since = self.get_last_successful_sync_time()
        return self.odoo_client.fetch_sale_orders(since=since)

    def sync_one(self, raw_record: dict[str, Any]) -> bool:
        domain = self.mapper.to_domain(raw_record)

        customer = self.contact_repo.get_by_odoo_id(domain.customer_odoo_id)
        if customer is None:
            # این خطا میره تو sync_logs و پردازش رکورد بعدی ادامه پیدا می‌کنه.
            # معمولاً یعنی Contactها هنوز sync نشدن -- باید همیشه اول Contacts،
            # بعد Sale Orders رو sync کنیم (ترتیب تو sync_orchestrator رعایت شده).
            raise ValueError(
                f"مشتری با odoo_id={domain.customer_odoo_id} در دیتابیس پیدا نشد."
            )

        _, created = self.repo.upsert(domain, customer_id=customer.id)
        return created
