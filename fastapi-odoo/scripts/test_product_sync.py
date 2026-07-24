from app.adapters.odoo_client import OdooClient
from app.adapters.product_adapter import ProductAdapter
from app.database.connection import SessionLocal
from app.repositories.product_repository import (
    ProductRepository,
)
from app.repositories.sync_repository import (
    SyncRepository,
)
from app.services.product_sync_service import (
    ProductSyncService,
)


client = OdooClient()
adapter = ProductAdapter(client)

with SessionLocal() as session:
    product_repository = ProductRepository(session)
    sync_repository = SyncRepository(session)

    service = ProductSyncService(
        adapter=adapter,
        product_repository=product_repository,
        sync_repository=sync_repository,
    )

    result = service.sync()

    session.commit()

    print(result)