from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, cast
from collections.abc import Generator
from contextlib import contextmanager

import pytest

from odoo_sync.application.ports.unit_of_work import UnitOfWork
from odoo_sync.application.services.shutdown import ShutdownFlag
from odoo_sync.application.services.sync_service import SyncService
from odoo_sync.domain.models import Contact
from odoo_sync.domain.read_outcome import ReadRecord
from odoo_sync.domain.sync import SyncStatus, SyncType, UpsertResult

pytestmark = pytest.mark.unit


class FakeErp:
    def get_upper_watermark(self) -> datetime:
        return datetime(2026, 7, 24, tzinfo=UTC)

    def iter_contacts(self, **_: Any) -> Any:
        yield ReadRecord(raw_id=1, value=Contact(1, "A", None, None, None, None))
        yield ReadRecord(raw_id=2, value=None, error=ValueError("bad password=secret"))
        yield ReadRecord(raw_id=3, value=Contact(3, "C", None, None, None, None))

    def iter_products(self, **_: Any) -> Any:
        return iter(())

    def iter_sale_orders(self, **_: Any) -> Any:
        return iter(())

    def iter_sale_order_lines(self, **_: Any) -> Any:
        return iter(())

class FakeSyncLock:
    @contextmanager
    def acquire(self) -> Generator[None]:
        yield

class FakeContacts:
    def find_id_by_odoo_id(self, odoo_id: int) -> int | None:
        return odoo_id

    def upsert(self, contact: Contact) -> UpsertResult:
        return UpsertResult.INSERTED if contact.odoo_id == 1 else UpsertResult.UNCHANGED


class FakeRuns:
    def __init__(self) -> None:
        self.finished_status: SyncStatus | None = None

    def start(self, **_: Any) -> int:
        return 42

    def finish(self, _run_id: int, *, status: SyncStatus, **_: Any) -> None:
        self.finished_status = status

    def latest_success_upper_watermark(self) -> datetime | None:
        return datetime(2026, 7, 23, tzinfo=UTC)


class FakeLogs:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def add(self, **kwargs: Any) -> None:
        self.messages.append(kwargs["error_message"])


class FakeUow:
    runs = FakeRuns()
    logs = FakeLogs()

    def __enter__(self) -> Any:
        self.contacts = FakeContacts()
        self.products = self.contacts
        self.sale_orders = self.contacts
        self.sale_order_lines = self.contacts
        self.sync_runs = self.runs
        self.sync_logs = self.logs
        return self

    def __exit__(self, *args: Any) -> None:
        self.rollback()

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


def test_sync_continues_after_record_error_and_sanitizes_log() -> None:
    service = SyncService(
        erp=FakeErp(),
        uow_factory=lambda: cast(UnitOfWork, FakeUow()),
        logger=logging.getLogger("test"),
        shutdown=ShutdownFlag(),
        sync_lock=FakeSyncLock(),
    )
    summary = service.sync(sync_type=SyncType.FULL, page_size=2)

    assert summary.status is SyncStatus.SUCCESS
    assert summary.counters.fetched == 3
    assert summary.counters.inserted == 1
    assert summary.counters.unchanged == 1
    assert summary.counters.failed == 1
    assert "secret" not in FakeUow.logs.messages[0]
