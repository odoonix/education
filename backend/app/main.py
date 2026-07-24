import logging
import signal
import sys
import time

from app.config.settings import get_settings
from app.logging_setup import setup_logging
from app.services.sync_orchestrator import run_full_sync

logger = logging.getLogger("main")

_shutdown_requested = False
settings = get_settings()


def _handle_shutdown_signal(signum, frame):  
    global _shutdown_requested
    logger.info("signal %s received; shutting down...", signum)
    _shutdown_requested = True


def _run_once() -> bool:
    try:
        stats = run_full_sync()
        logger.info("sync ended: %s", stats)
        return True
    except Exception:
        logger.exception("sync failed")
        return False


def main() -> None:
    setup_logging(settings.log_level)
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)
    signal.signal(signal.SIGINT, _handle_shutdown_signal)

    logger.info(
        "program started (run_mode=%s, interval=%ss, odoo_url=%s, odoo_db=%s)",
        settings.run_mode,
        settings.sync_interval_seconds,
        settings.ODOO_URL,
        settings.ODOO_DATABASE,
    )

    if settings.run_mode == "once":
        success = _run_once()
        sys.exit(0 if success else 1)

    # run_mode == "loop"
    while not _shutdown_requested:
        _run_once()

        waited = 0
        while waited < settings.sync_interval_seconds and not _shutdown_requested:
            time.sleep(1)
            waited += 1

    logger.info("program ended (gracefully)")
    sys.exit(0)


if __name__ == "__main__":
    main()
