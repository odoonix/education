from dependency_injector import containers, providers

from app.config.settings import settings
from app.infrastructure.odoo.client import OdooClient
from app.infrastructure.database.session import PostgreSQLConnection
from app.infrastructure.database.repositories.contact_repository import (
    SQLAlchemyContactRepository,
)
from app.infrastructure.database.repositories.product_repository import (
    SQLAlchemyProductRepository,
)
from app.infrastructure.database.repositories.sale_order_repository import (
    SQLAlchemySaleOrderRepository,
)
from app.infrastructure.database.repositories.sale_order_line_repository import (
    SQLAlchemySaleOrderLineRepository,
)
from app.infrastructure.database.repositories.sync_run_repository import (
    SQLAlchemySyncRunRepository,
)
from app.application.services.contact_sync_service import ContactSyncService
from app.application.services.product_sync_service import ProductSyncService
from app.application.services.sale_order_sync_service import SaleOrderSyncService
from app.application.services.sale_order_line_sync_service import (
    SaleOrderLineSyncService,
)
from app.application.use_cases.sync_entity_use_case import SyncEntityUseCase


def _build_odoo_client() -> OdooClient:
    client = OdooClient(
        url=settings.ODOO_URL,
        database=settings.ODOO_DB_NAME,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD,
    )
    client.authenticate()
    return client


class Container(containers.DeclarativeContainer):

    # Infrastructure / external adapters
    db_connection = providers.Singleton(PostgreSQLConnection)

    odoo_client = providers.Singleton(_build_odoo_client)

    # Repositories
    contact_repository = providers.Factory(
        SQLAlchemyContactRepository,
        db_connection=db_connection,
    )

    product_repository = providers.Factory(
        SQLAlchemyProductRepository,
        db_connection=db_connection,
    )

    sale_order_repository = providers.Factory(
        SQLAlchemySaleOrderRepository,
        db_connection=db_connection,
    )

    sale_order_line_repository = providers.Factory(
        SQLAlchemySaleOrderLineRepository,
        db_connection=db_connection,
    )

    sync_run_repository = providers.Factory(
        SQLAlchemySyncRunRepository,
        db_connection=db_connection,
    )

    # Sync services (Odoo readers)
    contact_sync_service = providers.Factory(
        ContactSyncService,
        odoo_client=odoo_client,
    )

    product_sync_service = providers.Factory(
        ProductSyncService,
        odoo_client=odoo_client,
    )

    sale_order_sync_service = providers.Factory(
        SaleOrderSyncService,
        odoo_client=odoo_client,
    )

    sale_order_line_sync_service = providers.Factory(
        SaleOrderLineSyncService,
        odoo_client=odoo_client,
    )

    # Use cases
    contact_sync_use_case = providers.Factory(
        SyncEntityUseCase,
        operation_type="contacts",
        source=contact_sync_service,
        repository=contact_repository,
        sync_run_repository=sync_run_repository,
    )

    product_sync_use_case = providers.Factory(
        SyncEntityUseCase,
        operation_type="products",
        source=product_sync_service,
        repository=product_repository,
        sync_run_repository=sync_run_repository,
    )

    sale_order_sync_use_case = providers.Factory(
        SyncEntityUseCase,
        operation_type="sale_orders",
        source=sale_order_sync_service,
        repository=sale_order_repository,
        sync_run_repository=sync_run_repository,
    )

    sale_order_line_sync_use_case = providers.Factory(
        SyncEntityUseCase,
        operation_type="sale_order_lines",
        source=sale_order_line_sync_service,
        repository=sale_order_line_repository,
        sync_run_repository=sync_run_repository,
    )
