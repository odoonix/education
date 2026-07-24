from dataclasses import dataclass

from app.application.use_cases.sync_entity_use_case import SyncEntityUseCase
from app.domain.entities.sync_run import SyncStatus
from app.domain.entities.sync_log import SyncLogLevel


@dataclass
class FakeEntity:
    odoo_id: int


class FakeSource:
    def __init__(self, entities=None, error=None):
        self._entities = entities or []
        self._error = error

    def sync(self):
        if self._error:
            raise self._error
        return self._entities


class FakeEntityRepo:
    def __init__(self, existing_ids=(), fail_on=()):
        self.saved = []
        self.updated = []
        self._existing = set(existing_ids)
        self._fail_on = set(fail_on)

    def get_by_odoo_id(self, odoo_id):
        return FakeEntity(odoo_id) if odoo_id in self._existing else None

    def save(self, entity):
        if entity.odoo_id in self._fail_on:
            raise ValueError(f"save failed for {entity.odoo_id}")
        self.saved.append(entity.odoo_id)

    def update(self, entity):
        if entity.odoo_id in self._fail_on:
            raise ValueError(f"update failed for {entity.odoo_id}")
        self.updated.append(entity.odoo_id)


class FakeSyncRunRepo:
    def __init__(self):
        self.logs = []
        self.finished = None
        self._seq = 0

    def create(self, run):
        self._seq += 1
        run.id = self._seq
        return run

    def finish(self, run):
        self.finished = run

    def add_log(self, log):
        self.logs.append(log)


def _use_case(source, repo, run_repo):
    return SyncEntityUseCase("contacts", source, repo, run_repo)


def test_all_new_records_are_saved():
    repo = FakeEntityRepo()
    run = _use_case(
        FakeSource([FakeEntity(1), FakeEntity(2), FakeEntity(3)]),
        repo,
        FakeSyncRunRepo(),
    ).execute()

    assert run.records_received == 3
    assert run.records_saved == 3
    assert run.records_updated == 0
    assert run.records_failed == 0
    assert run.status == SyncStatus.SUCCESS
    assert repo.saved == [1, 2, 3]


def test_existing_records_are_updated_not_duplicated():
    repo = FakeEntityRepo(existing_ids={1, 3})
    run = _use_case(
        FakeSource([FakeEntity(1), FakeEntity(2), FakeEntity(3)]),
        repo,
        FakeSyncRunRepo(),
    ).execute()

    assert run.records_saved == 1
    assert run.records_updated == 2
    assert run.status == SyncStatus.SUCCESS
    assert repo.saved == [2]
    assert repo.updated == [1, 3]


def test_record_error_is_isolated_logged_and_processing_continues():
    repo = FakeEntityRepo(fail_on={2})
    run_repo = FakeSyncRunRepo()
    run = _use_case(
        FakeSource([FakeEntity(1), FakeEntity(2), FakeEntity(3), FakeEntity(4)]),
        repo,
        run_repo,
    ).execute()

    assert run.records_received == 4
    assert run.records_saved == 3
    assert run.records_failed == 1
    assert run.status == SyncStatus.PARTIAL
    # record 4 was processed even though record 2 failed
    assert repo.saved == [1, 3, 4]
    assert len(run_repo.logs) == 1
    assert run_repo.logs[0].odoo_id == 2
    assert run_repo.logs[0].level == SyncLogLevel.ERROR


def test_all_records_failing_yields_failed_status():
    repo = FakeEntityRepo(fail_on={1, 2})
    run_repo = FakeSyncRunRepo()
    run = _use_case(
        FakeSource([FakeEntity(1), FakeEntity(2)]),
        repo,
        run_repo,
    ).execute()

    assert run.records_failed == 2
    assert run.records_saved == 0
    assert run.status == SyncStatus.FAILED
    assert len(run_repo.logs) == 2


def test_empty_source_is_success():
    run = _use_case(
        FakeSource([]), FakeEntityRepo(), FakeSyncRunRepo()
    ).execute()

    assert run.records_received == 0
    assert run.status == SyncStatus.SUCCESS


def test_fetch_failure_fails_the_run_and_is_logged():
    run_repo = FakeSyncRunRepo()
    run = _use_case(
        FakeSource(error=RuntimeError("odoo down")),
        FakeEntityRepo(),
        run_repo,
    ).execute()

    assert run.status == SyncStatus.FAILED
    assert run.records_received == 0
    assert len(run_repo.logs) == 1
    assert run_repo.logs[0].level == SyncLogLevel.ERROR
