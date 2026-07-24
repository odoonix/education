from fastapi import APIRouter

from app.container import create_full_sync_service
from app.database.connection import SessionLocal


router = APIRouter()


@router.post("/sync")
def run_sync() -> dict[str, int | str]:
    with SessionLocal() as session:
        try:
            full_sync_service = (
                create_full_sync_service(session)
            )

            sync_run = full_sync_service.sync()

            session.commit()

            return {
                "sync_run_id": sync_run.id,
                "status": sync_run.status,
                "contacts_processed": (
                    sync_run.contacts_processed
                ),
                "products_processed": (
                    sync_run.products_processed
                ),
                "sale_orders_processed": (
                    sync_run.sale_orders_processed
                ),
                "sale_order_lines_processed": (
                    sync_run.sale_order_lines_processed
                ),
            }

        except Exception:
            session.rollback()

            raise