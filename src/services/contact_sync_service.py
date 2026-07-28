from typing import Any

from src.mappers.contact_mapper import ContactMapper
from src.odoo_client.client import OdooClient
from src.repositories.contact_repository import ContactRepository
from src.services.base_sync_service import BaseSyncService


class ContactSyncService(BaseSyncService):
    operation_type = "contacts_sync"

    def __init__(self, session, odoo_client: OdooClient):
        super().__init__(session)
        self.odoo_client = odoo_client
        self.repo = ContactRepository(session)
        self.mapper = ContactMapper()

    def fetch_records(self) -> list[dict[str, Any]]:
        since = self.get_last_successful_sync_time()
        return self.odoo_client.fetch_contacts(since=since)

    def sync_one(self, raw_record: dict[str, Any]) -> bool:
        domain = self.mapper.to_domain(raw_record)
        _, created = self.repo.upsert(domain)
        return created
