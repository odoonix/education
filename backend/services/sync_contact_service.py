from adapters.odoo_adapter import OdooAdapter
from repositories.contact_repository import ContactRepository
from mappers.contact_mapper import map_contact
from services.sync_engine import SyncEngine



def sync_contacts(session, adapter: OdooAdapter, batch_size: int = 500, shutdown_handler=None) -> dict:
    repo = ContactRepository(session)
    engine = SyncEngine(
        session=session,
        operation_type="contacts_sync",
        count_fn=adapter.count_contacts,
        fetch_page_fn=adapter.get_contacts,
        map_fn=map_contact,
        upsert_fn=repo.upsert,
        batch_size=batch_size,
        shutdown_handler=shutdown_handler,
    )
    return engine.run()