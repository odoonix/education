from abc import ABC, abstractmethod

from app.domain.entities.sync_run import SyncRun
from app.domain.entities.sync_log import SyncLog


class SyncRunRepository(ABC):

    @abstractmethod
    def create(self, sync_run: SyncRun) -> SyncRun:
        pass

    @abstractmethod
    def finish(self, sync_run: SyncRun) -> None:
        pass

    @abstractmethod
    def add_log(self, sync_log: SyncLog) -> None:
        pass
