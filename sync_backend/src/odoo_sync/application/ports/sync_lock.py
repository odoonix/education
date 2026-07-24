from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Protocol


class ConcurrentSyncError(RuntimeError):
    """Raised when another synchronization process owns the sync lock."""


class SyncLock(Protocol):
    """Coordinates mutually exclusive synchronization executions."""

    def acquire(self) -> AbstractContextManager[None]:
        """Acquire the lock for the lifetime of the context."""
        ...
