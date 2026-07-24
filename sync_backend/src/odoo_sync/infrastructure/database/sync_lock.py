from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import Engine, text
from odoo_sync.application.ports.sync_lock import ConcurrentSyncError


class PostgresSyncLock:
    def __init__(self, engine: Engine, lock_key: int) -> None:
        self.engine = engine
        self.lock_key = lock_key

    @contextmanager
    def acquire(self) -> Iterator[None]:
        with self.engine.connect() as connection:
            acquired = connection.scalar(
                text("SELECT pg_try_advisory_lock(:key)"),
                {"key": self.lock_key},
            )

            if not acquired:
                raise ConcurrentSyncError(
                    "another sync process is already running"
                )

            try:
                yield
            finally:
                connection.execute(
                    text("SELECT pg_advisory_unlock(:key)"),
                    {"key": self.lock_key},
                )
