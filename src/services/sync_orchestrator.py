"""
ترتیب اجرا مهمه: Contacts و Products باید قبل از Sale Orders sync بشن (چون
Sale Order به customer_id نیاز داره)، و Sale Orders باید قبل از Sale Order
Lines sync بشه (چون هر line به یک order نیاز داره).
"""

from sqlalchemy.orm import Session

from src.db.models import SyncRun
from src.odoo_client.client import OdooClient
from src.services.contact_sync_service import ContactSyncService
from src.services.product_sync_service import ProductSyncService
from src.services.sale_order_sync_service import SaleOrderSyncService
from src.services.sale_order_line_sync_service import SaleOrderLineSyncService


class SyncOrchestrator:
    def __init__(self, session: Session, odoo_client: OdooClient):
        self.session = session
        self.odoo_client = odoo_client

    def run_all(self) -> list[SyncRun]:
        service_classes = [
            ContactSyncService,
            ProductSyncService,
            SaleOrderSyncService,
            SaleOrderLineSyncService,
        ]

        results: list[SyncRun] = []
        for service_cls in service_classes:
            service = service_cls(self.session, self.odoo_client)
            sync_run = service.run()
            results.append(sync_run)

        return results
