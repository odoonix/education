from app.adapters.contact_adapter import ContactAdapter
from app.models import SyncRun
from app.repositories.contact_repository import ContactRepository
from app.repositories.sync_repository import SyncRepository


class ContactSyncService:
    def __init__(
            self,
            adapter: ContactAdapter,
            contact_repository: ContactRepository,
            sync_repository: SyncRepository,
    ) -> None:
        self._adapter = adapter
        self._contact_repository = contact_repository
        self._sync_repository = sync_repository

    def sync(
            self,
            sync_run: SyncRun,
    ) -> int:
        processed_count = 0

        contacts = self._adapter.fetch_contacts()

        for contact_data in contacts:
            existing_contact = (
                self._contact_repository.get_by_odoo_id(
                    contact_data.odoo_id,
                )
            )

            if existing_contact is None:
                self._contact_repository.create(
                    contact_data,
                )

                action = "created"

            else:
                self._contact_repository.update(
                    existing_contact,
                    contact_data,
                )

                action = "updated"

            self._sync_repository.create_log(
                sync_run=sync_run,
                level="INFO",
                entity="contact",
                action=action,
                record_odoo_id=contact_data.odoo_id,
                message=(
                    f"Contact {contact_data.odoo_id} "
                    f"{action} successfully"
                ),
            )

            processed_count += 1

        sync_run.contacts_processed = processed_count

        return processed_count
