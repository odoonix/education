import logging
import signal
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.adapters.odoo_adapter import OdooAdapter
from backend.infrastructure.config import get_settings
from backend.services.sync_service import SyncService

logger = logging.getLogger("backend.cli")
_shutdown_requested = False


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )


def _handle_shutdown_signal(signum: int, _frame) -> None:
    global _shutdown_requested
    _shutdown_requested = True
    logger.warning("Received signal %s, will stop after current record finishes", signum)


def run_sync() -> int:
    configure_logging()
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)
    signal.signal(signal.SIGINT, _handle_shutdown_signal)

    settings = get_settings()
    engine = create_engine(settings.app_db_url)
    session_factory = sessionmaker(bind=engine)

    odoo = OdooAdapter(
        url=settings.odoo_url,
        db=settings.odoo_db,
        username=settings.odoo_username,
        password=settings.odoo_password,
    )

    session = session_factory()
    try:
        service = SyncService(session, odoo)
        run = service.run_full_sync()
        logger.info(
            "Sync finished: fetched=%s created=%s updated=%s errors=%s",
            run.fetched_count,
            run.created_count,
            run.updated_count,
            run.error_count,
        )
        return 0 if run.error_count == 0 else 1
    except Exception:
        logger.exception("Sync failed with an unhandled error")
        return 2
    finally:
        session.close()
        logger.info("Database session closed")


if __name__ == "__main__":
    sys.exit(run_sync())