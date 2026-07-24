import logging

from app.mapping.mappers import map_contact
from app.odoo_client.client import OdooClient
from app.repositories.contact_repository import ContactRepository
from app.services.stats import SyncStats
from app.services.sync_logger import SyncRunLogger

logger = logging.getLogger(__name__)

CONTACT_FIELDS = ["id", "name", "email", "phone", "mobile"]

CONTACT_DOMAIN: list = []


class ContactSyncService:
    def __init__(self, odoo_client: OdooClient, repository: ContactRepository):
        self.odoo_client = odoo_client
        self.repository = repository

    def sync(self, sync_run_logger: SyncRunLogger) -> SyncStats:
        stats = SyncStats()

        for raw in self.odoo_client.iter_all(
            "res.partner", CONTACT_DOMAIN, CONTACT_FIELDS, batch_size=100
        ):
            stats.fetched += 1
            odoo_id = raw["id"]
            try:
                data = map_contact(raw)
                _, created = self.repository.upsert(odoo_id, data)
                if created:
                    stats.created += 1
                else:
                    stats.updated += 1
            except Exception as exc:
                stats.failed += 1
                logger.exception("error processing contact with odoo_id=%s", odoo_id)
                sync_run_logger.log_error("contact", odoo_id, str(exc))
                continue

        return stats
