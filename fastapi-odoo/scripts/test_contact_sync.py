from app.adapters.contact_adapter import ContactAdapter
from app.adapters.odoo_client import OdooClient
from app.database.connection import SessionLocal
from app.repositories.contact_repository import (
    ContactRepository,
)
from app.repositories.sync_repository import (
    SyncRepository,
)
from app.services.contact_sync_service import (
    ContactSyncService,
)


client = OdooClient()
adapter = ContactAdapter(client)

with SessionLocal() as session:
    contact_repository = ContactRepository(session)
    sync_repository = SyncRepository(session)

    service = ContactSyncService(
        adapter=adapter,
        contact_repository=contact_repository,
        sync_repository=sync_repository,
    )

    result = service.sync()

    session.commit()

    print(result)