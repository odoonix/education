from app.adapters.odoo_client import OdooClient
from app.adapters.sale_order_adapter import SaleOrderAdapter
from app.database.connection import SessionLocal
from app.repositories.product_repository import (
    ProductRepository,
)
from app.repositories.sale_order_repository import (
    SaleOrderRepository,
)
from app.repositories.sale_order_line_repository import (
    SaleOrderLineRepository,
)
from app.repositories.sync_repository import (
    SyncRepository,
)
from app.services.sale_order_line_sync_service import (
    SaleOrderLineSyncService,
)


client = OdooClient()
adapter = SaleOrderAdapter(client)

with SessionLocal() as session:
    product_repository = ProductRepository(session)
    sale_order_repository = SaleOrderRepository(session)
    sale_order_line_repository = SaleOrderLineRepository(session)
    sync_repository = SyncRepository(session)

    service = SaleOrderLineSyncService(
        adapter=adapter,
        product_repository=product_repository,
        sale_order_repository=sale_order_repository,
        sale_order_line_repository=sale_order_line_repository,
        sync_repository=sync_repository,
    )

    result = service.sync()

    session.commit()

    print(result)