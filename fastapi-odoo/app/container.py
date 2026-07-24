from app.adapters.contact_adapter import ContactAdapter
from app.adapters.odoo_client import OdooClient
from app.adapters.product_adapter import ProductAdapter
from app.adapters.sale_order_adapter import SaleOrderAdapter
from app.repositories.contact_repository import ContactRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_order_line_repository import (
    SaleOrderLineRepository,
)
from app.repositories.sale_order_repository import (
    SaleOrderRepository,
)
from app.repositories.sync_repository import SyncRepository
from app.services.contact_sync_service import (
    ContactSyncService,
)
from app.services.full_sync_service import (
    FullSyncService,
)
from app.services.product_sync_service import (
    ProductSyncService,
)
from app.services.sale_order_line_sync_service import (
    SaleOrderLineSyncService,
)
from app.services.sale_order_sync_service import (
    SaleOrderSyncService,
)

def create_full_sync_service(
    session,
) -> FullSyncService:
    odoo_client = OdooClient()

    sync_repository = SyncRepository(session)

    contact_repository = ContactRepository(session)

    product_repository = ProductRepository(session)

    sale_order_repository = SaleOrderRepository(
        session,
    )

    sale_order_line_repository = (
        SaleOrderLineRepository(session)
    )

    contact_adapter = ContactAdapter(
        odoo_client,
    )

    product_adapter = ProductAdapter(
        odoo_client,
    )

    sale_order_adapter = SaleOrderAdapter(
        odoo_client,
    )

    contact_sync_service = ContactSyncService(
        adapter=contact_adapter,
        contact_repository=contact_repository,
        sync_repository=sync_repository,
    )

    product_sync_service = ProductSyncService(
        adapter=product_adapter,
        product_repository=product_repository,
        sync_repository=sync_repository,
    )

    sale_order_sync_service = SaleOrderSyncService(
        adapter=sale_order_adapter,
        contact_repository=contact_repository,
        sale_order_repository=sale_order_repository,
        sync_repository=sync_repository,
    )

    sale_order_line_sync_service = (
        SaleOrderLineSyncService(
            adapter=sale_order_adapter,
            product_repository=product_repository,
            sale_order_repository=sale_order_repository,
            sale_order_line_repository=(
                sale_order_line_repository
            ),
            sync_repository=sync_repository,
        )
    )

    return FullSyncService(
        sync_repository=sync_repository,
        contact_sync_service=contact_sync_service,
        product_sync_service=product_sync_service,
        sale_order_sync_service=sale_order_sync_service,
        sale_order_line_sync_service=(
            sale_order_line_sync_service
        ),
    )