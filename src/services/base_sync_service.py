"""
BaseSyncService قلب مدیریت خطا و Logging پروژه‌ست.

نکته‌ی مهم فنی: چرا از session.begin_nested() استفاده کردیم؟
------------------------------------------------------------
همه‌ی رکوردهای یک Sync تو یک Session/Transaction مشترک پردازش میشن (برای
اینکه سریع‌تر باشه، مجبور نباشیم برای هر رکورد یه Transaction جدا باز کنیم).
اما مشکل اینجاست: اگه رکورد ۳ خطا بده و بخوایم session.rollback() کنیم،
این کل Transaction رو rollback می‌کنه — یعنی رکورد ۱ و ۲ که موفق بودن هم
از بین میرن!

راه‌حل: SAVEPOINT (با session.begin_nested()). قبل از هر رکورد یک "نقطه‌ی
برگشت کوچیک" باز می‌کنیم. اگه اون رکورد خطا داد، فقط تا همون نقطه برمی‌گردیم،
بدون اینکه رکوردهای قبلی که موفق بودن رو از دست بدیم. این دقیقاً همون
رفتاریه که سناریوی آزمون خواسته:
    Record 1 -> Success, Record 2 -> Success, Record 3 -> Error,
    Record 4 -> Success, Record 5 -> Success  (پردازش متوقف نمیشه)
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import Any

from sqlalchemy.orm import Session

from src.db.models import SyncRun, SyncLog

logger = logging.getLogger(__name__)


class BaseSyncService(ABC):
    #: هر Service فرزند این رو ست می‌کنه، مثلاً "contacts_sync"
    operation_type: str

    def __init__(self, session: Session):
        self.session = session

    # ---------- هر Service فرزند این دو متد رو پیاده‌سازی می‌کنه ----------
    @abstractmethod
    def fetch_records(self) -> list[dict[str, Any]]:
        """رکوردهای خام رو از Odoo می‌گیره."""
        raise NotImplementedError

    @abstractmethod
    def sync_one(self, raw_record: dict[str, Any]) -> bool:
        """
        یک رکورد رو Map و در دیتابیس Upsert می‌کنه.
        خروجی: True اگه رکورد جدید بود، False اگه آپدیت شد.
        """
        raise NotImplementedError

    def get_last_successful_sync_time(self) -> datetime | None:
        """
        زمان شروع آخرین اجرای موفق (یا partial_success) همین operation_type
        رو برمی‌گردونه. Serviceهای فرزند از این برای Incremental Sync
        استفاده می‌کنن -- یعنی به‌جای خوندن کل داده‌ی Odoo، فقط رکوردهایی
        که از آخرین Sync موفق به بعد تغییر کردن رو می‌خونن.
        اگه قبلاً هیچ Sync موفقی نبوده (اولین اجرا)، None برمی‌گردونه که
        یعنی «همه‌چیز رو بخون» (Full Sync).
        """
        last_run = (
            self.session.query(SyncRun)
            .filter(
                SyncRun.operation_type == self.operation_type,
                SyncRun.status.in_(["success", "partial_success"]),
            )
            .order_by(SyncRun.started_at.desc())
            .first()
        )
        return last_run.started_at if last_run else None

    # ---------- orchestration مشترک ----------
    def run(self) -> SyncRun:
        logger.info(f"شروع Sync: {self.operation_type}")

        sync_run = SyncRun(
            operation_type=self.operation_type,
            started_at=datetime.utcnow(),
            status="running",
        )
        self.session.add(sync_run)
        self.session.flush()  # الان sync_run.id در دسترسه

        try:
            records = self.fetch_records()
        except Exception as exc:
            logger.error(f"[{self.operation_type}] دریافت داده از Odoo شکست خورد: {exc}")
            self._log(sync_run, "ERROR", f"دریافت داده از Odoo شکست خورد: {exc}")
            sync_run.status = "failed"
            sync_run.finished_at = datetime.utcnow()
            self.session.commit()
            raise

        sync_run.records_fetched = len(records)

        created = updated = failed = 0

        try:
            for raw_record in records:
                record_id = raw_record.get("id", "?")
                try:
                    with self.session.begin_nested():  # SAVEPOINT مخصوص همین رکورد
                        was_created = self.sync_one(raw_record)
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as exc:
                    failed += 1
                    logger.warning(f"[{self.operation_type}] خطا در رکورد odoo_id={record_id}: {exc}")
                    self._log(
                        sync_run, "ERROR",
                        f"خطا در پردازش رکورد: {exc}",
                        record_reference=f"odoo_id={record_id}",
                    )
                    # پردازش رکورد بعدی ادامه پیدا می‌کنه (continue ضمنیه، حلقه ادامه داره)
        except KeyboardInterrupt:
            # Graceful Shutdown: وقتی Ctrl+C یا سیگنال توقف (SIGTERM از
            # docker stop) میاد، به‌جای اینکه بدون هیچ ثبتی بمیریم، وضعیت
            # فعلی (چندتا رکورد تا الان موفق/ناموفق بودن) رو ذخیره می‌کنیم
            # و sync_run رو با status="cancelled" می‌بندیم -- بعداً اگه
            # دوباره اجرا بشه، Idempotency تضمین می‌کنه چیزی خراب/دوتا نشه.
            logger.warning(f"[{self.operation_type}] سیگنال توقف دریافت شد؛ بستن تمیز Sync...")
            sync_run.records_created = created
            sync_run.records_updated = updated
            sync_run.records_failed = failed
            sync_run.status = "cancelled"
            sync_run.finished_at = datetime.utcnow()
            self.session.commit()
            raise

        sync_run.records_created = created
        sync_run.records_updated = updated
        sync_run.records_failed = failed
        sync_run.status = "success" if failed == 0 else "partial_success"
        sync_run.finished_at = datetime.utcnow()

        self.session.commit()

        logger.info(
            f"پایان Sync: {self.operation_type} | "
            f"fetched={sync_run.records_fetched} created={created} "
            f"updated={updated} failed={failed} status={sync_run.status}"
        )
        return sync_run

    def _log(self, sync_run: SyncRun, level: str, message: str, record_reference: str | None = None):
        self.session.add(
            SyncLog(
                sync_run_id=sync_run.id,
                level=level,
                message=message,
                record_reference=record_reference,
            )
        )
