from unittest.mock import MagicMock

from app.services.contact_sync import ContactSyncService


def _fake_client(rows):
    client = MagicMock()
    client.iter_all.return_value = iter(rows)
    return client


def test_sync_creates_and_updates_correctly():
    client = _fake_client(
        [
            {"id": 1, "name": "Ali", "email": "ali@x.com", "phone": None, "mobile": None},
            {"id": 2, "name": "Sara", "email": "sara@x.com", "phone": None, "mobile": None},
        ]
    )
    repo = MagicMock()
    repo.upsert.side_effect = [
        (MagicMock(), True),   
        (MagicMock(), False),  
    ]

    service = ContactSyncService(client, repo)
    stats = service.sync(sync_run_logger=MagicMock())

    assert stats.fetched == 2
    assert stats.created == 1
    assert stats.updated == 1
    assert stats.failed == 0
    assert repo.upsert.call_count == 2


def test_sync_continues_after_a_single_record_error():
    client = _fake_client(
        [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 3, "name": "C"},
        ]
    )
    repo = MagicMock()
    repo.upsert.side_effect = [
        (MagicMock(), True),
        Exception("db exploded"),
        (MagicMock(), True),
    ]

    sync_run_logger = MagicMock()
    service = ContactSyncService(client, repo)
    stats = service.sync(sync_run_logger=sync_run_logger)

    assert stats.fetched == 3
    assert stats.created == 2
    assert stats.failed == 1
    assert repo.upsert.call_count == 3
    sync_run_logger.log_error.assert_called_once_with("contact", 2, "db exploded")


def test_sync_with_no_contacts_returns_zero_stats():
    client = _fake_client([])
    repo = MagicMock()

    service = ContactSyncService(client, repo)
    stats = service.sync(sync_run_logger=MagicMock())

    assert stats.as_dict() == {"fetched": 0, "created": 0, "updated": 0, "failed": 0}
    repo.upsert.assert_not_called()


def test_sync_passes_mapped_data_to_repository():
    client = _fake_client(
        [{"id": 1, "name": "Ali", "email": "ali@x.com", "phone": "111", "mobile": "222"}]
    )
    repo = MagicMock()
    repo.upsert.return_value = (MagicMock(), True)

    service = ContactSyncService(client, repo)
    service.sync(sync_run_logger=MagicMock())

    repo.upsert.assert_called_once_with(
        1, {"name": "Ali", "email": "ali@x.com", "phone": "111", "mobile": "222"}
    )
