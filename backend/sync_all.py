"""
نقطه ورود اجرای کامل Sync — به ترتیب درستِ وابستگی‌ها.
"""
from adapters.odoo_adapter import OdooAdapter
from core.config import get_settings
from core.logger import configure_logging, get_logger
from database.session import SessionLocal
from services.sync_contact_service import sync_contacts
from services.sync_product_service import sync_products
from services.sync_sale_order_service import sync_sale_orders
from services.sync_sale_order_line_service import sync_sale_order_lines
from core.shutdown import ShutdownHandler


def main():
    configure_logging()
    logger = get_logger("sync_all")
    settings = get_settings()


    shutdown_handler = ShutdownHandler()

    adapter = OdooAdapter(settings.odoo_url, settings.odoo_db, settings.odoo_username, settings.odoo_password)
    session = SessionLocal()


    try:
        results = []
        results.append(sync_contacts(session, adapter, shutdown_handler=shutdown_handler))
        if shutdown_handler.shutdown_requested:
            return
        results.append(sync_products(session, adapter, shutdown_handler=shutdown_handler))
        if shutdown_handler.shutdown_requested:
            return
        results.append(sync_sale_orders(session, adapter, shutdown_handler=shutdown_handler))
        if shutdown_handler.shutdown_requested:
            return
        results.append(sync_sale_order_lines(session, adapter, shutdown_handler=shutdown_handler))

        for r in results:
            logger.info("sync_summary: %s", r)
    finally:
        session.close()


if __name__ == "__main__":
    main()