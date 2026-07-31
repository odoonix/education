from __future__ import annotations

import pytest
from sqlalchemy import create_engine

from odoo_sync.application.ports.sync_lock import ConcurrentSyncError
from odoo_sync.config import Settings
from odoo_sync.infrastructure.database.sync_lock import PostgresSyncLock

pytestmark = pytest.mark.integration


def test_second_process_cannot_acquire_same_sync_lock() -> None:
    settings = Settings()
    engine = create_engine(
        settings.sync_database_url,
        pool_pre_ping=True,
    )

    first_lock = PostgresSyncLock(
        engine=engine,
        lock_key=settings.sync_lock_key,
    )
    second_lock = PostgresSyncLock(
        engine=engine,
        lock_key=settings.sync_lock_key,
    )

    with first_lock.acquire():
        with pytest.raises(
            ConcurrentSyncError,
            match="another sync process is already running",
        ):
            with second_lock.acquire():
                pytest.fail("second lock must not be acquired")

    with second_lock.acquire():
        pass

    engine.dispose()
