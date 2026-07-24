import logging
from datetime import datetime, timezone
from typing import Callable, Optional

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.db.models import SyncRun
from app.db.session import get_session
from app.odoo_client.client import OdooClient
from app.repositories.contact_repository import ContactRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_order_line_repository import SaleOrderLineRepository
from app.repositories.sale_order_repository import SaleOrderRepository
from app.services.contact_sync import ContactSyncService
from app.services.product_sync import ProductSyncService
from app.services.sale_order_sync import SaleOrderSyncService
from app.services.stats import SyncStats
from app.services.sync_logger import SyncRunLogger

logger = logging.getLogger(__name__)

settings = get_settings()

def _build_default_odoo_client() -> OdooClient:
    client = OdooClient(
        url=settings.ODOO_URL,
        db=settings.ODOO_DATABASE,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD,
    )
    client.authenticate()
    return client


def run_full_sync(
    odoo_client: Optional[OdooClient] = None,
    session_factory: Optional[Callable[[], Session]] = None,
) -> dict:
    session_factory = session_factory or get_session
    session = session_factory()
    total_stats = SyncStats()

    try:
        odoo_client = odoo_client or _build_default_odoo_client()

        sync_run_logger = SyncRunLogger(session, operation_type="full_sync")
        sync_run_id = sync_run_logger.sync_run.id
        session.commit()

        contact_repo = ContactRepository(session)
        product_repo = ProductRepository(session)
        sale_order_repo = SaleOrderRepository(session)
        sale_order_line_repo = SaleOrderLineRepository(session)

        contact_service = ContactSyncService(odoo_client, contact_repo)
        product_service = ProductSyncService(odoo_client, product_repo)
        sale_order_service = SaleOrderSyncService(
            odoo_client,
            sale_order_repo,
            sale_order_line_repo,
            contact_repo,
            product_repo,
        )

        try:
            total_stats.merge(contact_service.sync(sync_run_logger))
            session.commit()

            total_stats.merge(product_service.sync(sync_run_logger))
            session.commit()

            total_stats.merge(sale_order_service.sync(sync_run_logger))
            session.commit()

            sync_run_logger.finish("success", total_stats.as_dict())
            session.commit()

        except Exception:
            session.rollback()
            logger.exception("sync got an exception and rolled back")
            failure_session = session_factory()
            try:
                sync_run = failure_session.get(SyncRun, sync_run_id)
                if sync_run is not None:
                    sync_run.finished_at = datetime.now(timezone.utc)
                    sync_run.received_count = total_stats.fetched
                    sync_run.created_count = total_stats.created
                    sync_run.updated_count = total_stats.updated
                    sync_run.failed_count = total_stats.failed
                    failure_session.commit()
            finally:
                failure_session.close()
            raise
                
        return total_stats.as_dict()

    finally:
        session.close()
