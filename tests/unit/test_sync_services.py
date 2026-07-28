"""
تست‌های Service Layer با Mock کردن OdooClient — یعنی اصلاً به Odoo واقعی
وصل نمی‌شیم، فقط یک شیء تقلبی (Mock) می‌سازیم که داده‌ی از‌پیش‌مشخص برمی‌گردونه.
این باعث میشه تست‌ها سریع، پایدار (Odoo روشن باشه یا نه فرقی نمی‌کنه) و
قابل‌کنترل (می‌تونیم عمداً داده‌ی خراب بدیم) باشن.
"""

from unittest.mock import MagicMock

import pytest

from src.db.models import SyncLog, SyncRun
from src.services.contact_sync_service import ContactSyncService
from src.services.product_sync_service import ProductSyncService
from src.services.sale_order_sync_service import SaleOrderSyncService


def test_contact_sync_creates_new_records(session):
    fake_odoo = MagicMock()
    fake_odoo.fetch_contacts.return_value = [
        {"id": 1, "name": "Ali", "email": "ali@example.com", "phone": False, "mobile": False},
        {"id": 2, "name": "Sara", "email": "sara@example.com", "phone": False, "mobile": False},
    ]

    service = ContactSyncService(session, fake_odoo)
    sync_run = service.run()

    assert sync_run.status == "success"
    assert sync_run.records_fetched == 2
    assert sync_run.records_created == 2
    assert sync_run.records_failed == 0


def test_contact_sync_continues_after_one_record_fails(session):
    """
    مهم‌ترین تست پروژه از نظر مدیریت خطا:
    Record 1 -> موفق، Record 2 -> خراب (فیلد name نداره)، Record 3 -> موفق.
    طبق سناریوی آزمون، پردازش نباید بعد از خطای رکورد ۲ متوقف بشه.
    """
    fake_odoo = MagicMock()
    fake_odoo.fetch_contacts.return_value = [
        {"id": 1, "name": "Ali", "email": "ali@example.com", "phone": False, "mobile": False},
        {"id": 2, "email": "broken@example.com"},  # عمداً فیلد "name" رو حذف کردیم تا خطا بده
        {"id": 3, "name": "Reza", "email": "reza@example.com", "phone": False, "mobile": False},
    ]

    service = ContactSyncService(session, fake_odoo)
    sync_run = service.run()

    assert sync_run.records_fetched == 3
    assert sync_run.records_created == 2   # رکورد ۱ و ۳
    assert sync_run.records_failed == 1     # رکورد ۲
    assert sync_run.status == "partial_success"

    # خطا باید تو sync_logs هم ثبت شده باشه
    logs = session.query(SyncLog).filter_by(sync_run_id=sync_run.id).all()
    assert len(logs) == 1
    assert logs[0].level == "ERROR"
    assert "odoo_id=2" in logs[0].record_reference


def test_contact_sync_is_idempotent_across_two_runs(session):
    """اجرای Service دوبار پشت‌سرهم نباید رکورد تکراری بسازه."""
    fake_odoo = MagicMock()
    fake_odoo.fetch_contacts.return_value = [
        {"id": 1, "name": "Ali", "email": "ali@example.com", "phone": False, "mobile": False},
    ]

    first_run = ContactSyncService(session, fake_odoo).run()
    assert first_run.records_created == 1
    assert first_run.records_updated == 0

    second_run = ContactSyncService(session, fake_odoo).run()
    assert second_run.records_created == 0
    assert second_run.records_updated == 1


def test_product_sync_creates_new_records(session):
    fake_odoo = MagicMock()
    fake_odoo.fetch_products.return_value = [
        {"id": 1, "name": "Mouse", "default_code": "PRD-001", "list_price": 25.0, "type": "consu"},
        {"id": 2, "name": "Keyboard", "default_code": "PRD-002", "list_price": 75.0, "type": "consu"},
    ]

    sync_run = ProductSyncService(session, fake_odoo).run()

    assert sync_run.status == "success"
    assert sync_run.records_created == 2
    assert sync_run.records_failed == 0


def test_sale_order_sync_fails_gracefully_when_customer_missing():
    """
    اگه Sale Order به مشتری‌ای اشاره کنه که هنوز sync نشده، نباید کل برنامه
    کرش کنه — باید به‌عنوان یک رکورد ناموفق ثبت بشه و ادامه پیدا کنه.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.db.models import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    local_session = sessionmaker(bind=engine)()

    fake_odoo = MagicMock()
    fake_odoo.fetch_sale_orders.return_value = [
        {
            "id": 10, "name": "S00001",
            "partner_id": [999, "Unknown Customer"],  # این مشتری تو دیتابیس ما نیست
            "date_order": "2026-06-01 10:00:00",
            "state": "sale", "amount_total": 50.0,
        },
    ]

    sync_run = SaleOrderSyncService(local_session, fake_odoo).run()

    assert sync_run.records_fetched == 1
    assert sync_run.records_failed == 1
    assert sync_run.records_created == 0
    assert sync_run.status == "partial_success"


def test_incremental_sync_passes_last_run_time_on_second_call(session):
    """
    اجرای اول باید since=None (یعنی Full Sync) صدا بزنه. اجرای دوم باید
    since رو برابر زمان شروع اجرای اول بده -- یعنی Incremental Sync.
    """
    fake_odoo = MagicMock()
    fake_odoo.fetch_contacts.return_value = [
        {"id": 1, "name": "Ali", "email": "ali@example.com", "phone": False, "mobile": False},
    ]

    first_run = ContactSyncService(session, fake_odoo).run()
    fake_odoo.fetch_contacts.assert_called_with(since=None)

    ContactSyncService(session, fake_odoo).run()
    _, kwargs = fake_odoo.fetch_contacts.call_args
    assert kwargs["since"] == first_run.started_at


def test_graceful_shutdown_marks_sync_run_as_cancelled(session):
    """
    اگه وسط پردازش یه KeyboardInterrupt (شبیه‌ساز Ctrl+C یا SIGTERM) بیاد،
    نباید بدون هیچ ثبتی بمیره -- باید sync_run با status='cancelled' و
    آماری که تا همون‌جا جمع شده ذخیره بشه.
    """
    fake_odoo = MagicMock()
    fake_odoo.fetch_contacts.return_value = [
        {"id": 1, "name": "Ali", "email": "ali@example.com", "phone": False, "mobile": False},
        {"id": 2, "name": "Sara", "email": "sara@example.com", "phone": False, "mobile": False},
    ]

    service = ContactSyncService(session, fake_odoo)

    original_sync_one = service.sync_one
    call_count = {"n": 0}

    def flaky_sync_one(raw_record):
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise KeyboardInterrupt()
        return original_sync_one(raw_record)

    service.sync_one = flaky_sync_one

    with pytest.raises(KeyboardInterrupt):
        service.run()

    saved_run = session.query(SyncRun).filter_by(operation_type="contacts_sync").first()
    assert saved_run.status == "cancelled"
    assert saved_run.records_created == 1  # رکورد ۱ قبل از وقفه موفق شده بود
