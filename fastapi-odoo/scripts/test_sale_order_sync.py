from app.adapters.odoo_client import OdooClient
from app.adapters.sale_order_adapter import SaleOrderAdapter
from app.database.connection import SessionLocal
from app.repositories.contact_repository import (
    ContactRepository,
)
from app.repositories.sale_order_repository import (
    SaleOrderRepository,
)
from app.repositories.sync_repository import (
    SyncRepository,
)
from app.services.sale_order_sync_service import (
    SaleOrderSyncService,
)

client = OdooClient()
adapter = SaleOrderAdapter(client)

with SessionLocal() as session:
    contact_repository = ContactRepository(session)
    sale_order_repository = SaleOrderRepository(session)
    sync_repository = SyncRepository(session)

    service = SaleOrderSyncService(
        adapter=adapter,
        contact_repository=contact_repository,
        sale_order_repository=sale_order_repository,
        sync_repository=sync_repository,
    )

    result = service.sync()

    session.commit()

    print(result)