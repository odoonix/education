"""
نقطه‌ی ورود اصلی پروژه. کل فرآیند Sync رو یک‌جا اجرا می‌کنه.

اجرا:
    python -m src.main
"""

import logging
import signal

from src.core.logging_config import setup_logging
from src.db.session import get_session
from src.odoo_client.client import build_odoo_client
from src.services.sync_orchestrator import SyncOrchestrator

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    # Graceful Shutdown: وقتی docker stop یا Ctrl+C بزنی، سیستم عامل سیگنال
    # SIGTERM/SIGINT می‌فرسته. با ثبت signal.default_int_handler، این سیگنال
    # تبدیل به KeyboardInterrupt میشه -- که BaseSyncService از قبل بلده
    # درست مدیریتش کنه (رکورد فعلی رو تموم می‌کنه، وضعیت رو تو sync_runs
    # با status="cancelled" ذخیره می‌کنه، بعد تمیز می‌بنده).
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    session = get_session()
    odoo_client = build_odoo_client()

    orchestrator = SyncOrchestrator(session, odoo_client)

    try:
        results = orchestrator.run_all()
        print("\n========== نتیجه‌ی Sync ==========")
        for r in results:
            print(
                f"{r.operation_type:25s} | "
                f"fetched={r.records_fetched:3d}  "
                f"created={r.records_created:3d}  "
                f"updated={r.records_updated:3d}  "
                f"failed={r.records_failed:3d}  "
                f"status={r.status}"
            )
        print("===================================\n")
    except KeyboardInterrupt:
        logger.warning("Sync به‌خاطر سیگنال توقف (Ctrl+C یا docker stop) متوقف شد.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
