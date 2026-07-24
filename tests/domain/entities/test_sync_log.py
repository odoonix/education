from app.domain.entities.sync_log import SyncLog, SyncLogLevel


def test_create_sync_log():
    log = SyncLog(
        sync_run_id=1,
        level=SyncLogLevel.ERROR,
        message="failed to save record",
        odoo_id=42,
    )

    assert log.sync_run_id == 1
    assert log.level == SyncLogLevel.ERROR
    assert log.message == "failed to save record"
    assert log.odoo_id == 42
    assert log.created_at is None
    assert log.id is None
