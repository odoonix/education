"""
SyncRunLogger tests on a real database.
Here we actually verify that records are correctly saved in the sync_runs and sync_logs
tables - not just that the methods have been called.
"""
import pytest

from app.db.models import SyncLog, SyncRun
from app.services.sync_logger import SyncRunLogger

pytestmark = pytest.mark.db


def test_creates_sync_run_on_init(db_session):
    logger = SyncRunLogger(db_session, operation_type="full_sync")
    db_session.commit()

    runs = db_session.query(SyncRun).all()
    assert len(runs) == 1
    assert runs[0].id == logger.sync_run.id


def test_log_error_persists_to_sync_logs(db_session):
    logger = SyncRunLogger(db_session, operation_type="full_sync")
    logger.log_error("contact", 42, "something went wrong")
    db_session.commit()

    logs = db_session.query(SyncLog).all()
    assert len(logs) == 1
    assert logs[0].level == "error"
    assert logs[0].entity_type == "contact"
    assert logs[0].entity_odoo_id == 42
    assert logs[0].error_message == "something went wrong"
    assert logs[0].sync_run_id == logger.sync_run.id


def test_log_warning_and_info_use_correct_levels(db_session):
    logger = SyncRunLogger(db_session, operation_type="full_sync")
    logger.log_warning("careful", entity_type="product", entity_odoo_id=1)
    logger.log_info("all good", entity_type="product", entity_odoo_id=2)
    db_session.commit()

    logs = {log.level: log for log in db_session.query(SyncLog).all()}
    assert "warning" in logs
    assert "info" in logs
    assert logs["warning"].entity_odoo_id == 1
    assert logs["info"].entity_odoo_id == 2


def test_finish_updates_status_and_stats(db_session):
    logger = SyncRunLogger(db_session, operation_type="full_sync")
    logger.finish("success", {"fetched": 10, "created": 6, "updated": 3, "failed": 1})
    db_session.commit()

    run = db_session.query(SyncRun).one()
    assert run.finished_at is not None
    assert run.received_count == 10
    assert run.created_count == 6
    assert run.updated_count == 3
    assert run.failed_count == 1


def test_multiple_sync_runs_have_independent_logs(db_session):
    run1 = SyncRunLogger(db_session, operation_type="contacts_sync")
    run1.log_error("contact", 1, "err in run 1")
    db_session.commit()

    run2 = SyncRunLogger(db_session, operation_type="products_sync")
    run2.log_error("product", 2, "err in run 2")
    db_session.commit()

    run1_logs = db_session.query(SyncLog).filter_by(sync_run_id=run1.sync_run.id).all()
    run2_logs = db_session.query(SyncLog).filter_by(sync_run_id=run2.sync_run.id).all()

    assert len(run1_logs) == 1
    assert len(run2_logs) == 1
    assert run1_logs[0].error_message == "err in run 1"
    assert run2_logs[0].error_message == "err in run 2"
