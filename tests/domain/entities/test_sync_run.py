from datetime import datetime

from app.domain.entities.sync_run import SyncRun, SyncStatus


def test_create_sync_run():
    started = datetime(2026, 7, 24, 10, 0, 0)
    run = SyncRun(
        operation_type="contacts",
        started_at=started,
    )

    assert run.operation_type == "contacts"
    assert run.started_at == started
    assert run.status == SyncStatus.RUNNING
    assert run.records_received == 0
    assert run.records_saved == 0
    assert run.records_updated == 0
    assert run.records_failed == 0
    assert run.finished_at is None
    assert run.id is None
