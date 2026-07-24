import logging

from app.mapping.mappers import map_product
from app.odoo_client.client import OdooClient
from app.repositories.product_repository import ProductRepository
from app.services.stats import SyncStats
from app.services.sync_logger import SyncRunLogger

logger = logging.getLogger(__name__)

PRODUCT_FIELDS = [
    "id",
    "name",
    "default_code",
    "list_price",
    "type",
]
PRODUCT_DOMAIN: list = []


class ProductSyncService:
    def __init__(self, odoo_client: OdooClient, repository: ProductRepository):
        self.odoo_client = odoo_client
        self.repository = repository

    def sync(self, sync_run_logger: SyncRunLogger) -> SyncStats:
        stats = SyncStats()

        for raw in self.odoo_client.iter_all(
            "product.product", PRODUCT_DOMAIN, PRODUCT_FIELDS, batch_size=100
        ):
            stats.fetched += 1
            odoo_id = raw["id"]
            try:
                data = map_product(raw)
                _, created = self.repository.upsert(odoo_id, data)
                if created:
                    stats.created += 1
                else:
                    stats.updated += 1
            except Exception as exc:
                stats.failed += 1
                logger.exception("error processing product with odoo_id=%s", odoo_id)
                sync_run_logger.log_error("product", odoo_id, str(exc))
                continue

        return stats
