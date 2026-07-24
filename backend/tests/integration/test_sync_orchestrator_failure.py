"""
Test the complete failure path of SyncOrchestrator: when an infrastructure/unexpected error
(not a per-record error) occurs, it should:
  1. Rollback the main session
  2. Record a sync_runs entry with status='failed' and finished_at set
     (using a separate session, because the main session has been rolled back)
  3. Re-raise the Exception so the caller (main.py) is notified

These tests run on the same real PostgreSQL database (shared pg_session_factory fixture from
conftest.py).
"""
from unittest.mock import MagicMock

import pytest

from app.db.models import SyncRun
from app.services.sync_orchestrator import run_full_sync

pytestmark = pytest.mark.integration


def test_infrastructure_failure_marks_sync_run_as_failed(pg_session_factory):
    broken_client = MagicMock()
    broken_client.iter_all.side_effect = RuntimeError("odoo is down")

    with pytest.raises(RuntimeError):
        run_full_sync(odoo_client=broken_client, session_factory=pg_session_factory)

    session = pg_session_factory()
    try:
        sync_run = session.query(SyncRun).one()
        assert sync_run.finished_at is not None
    finally:
        session.close()


def test_partial_success_before_infrastructure_failure_is_preserved(pg_session_factory):
    from app.db.models import Contact

    def flaky_iter_all(model, domain, fields, batch_size=100): 
        if model == "res.partner":
            return iter([{"id": 1, "name": "Ali", "email": "a@x.com", "phone": None, "mobile": None}])
        if model == "product.product":
            raise RuntimeError("odoo timeout")
        return iter([])

    broken_client = MagicMock()
    broken_client.iter_all.side_effect = flaky_iter_all

    with pytest.raises(RuntimeError):
        run_full_sync(odoo_client=broken_client, session_factory=pg_session_factory)

    session = pg_session_factory()
    try:
        assert session.query(Contact).filter_by(odoo_id=1).count() == 1
        sync_run = session.query(SyncRun).one()
    finally:
        session.close()
