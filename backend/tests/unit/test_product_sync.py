from unittest.mock import MagicMock

from app.services.product_sync import ProductSyncService


def _fake_client(rows):
    client = MagicMock()
    client.iter_all.return_value = iter(rows)
    return client


def test_sync_creates_and_updates_correctly():
    client = _fake_client(
        [
            {"id": 7, "name": "Laptop", "default_code": "SKU-A", "list_price": 1000, "type": "consu"},
            {"id": 8, "name": "Mouse", "default_code": "SKU-B", "list_price": 50, "type": "consu"},
        ]
    )
    repo = MagicMock()
    repo.upsert.side_effect = [(MagicMock(), True), (MagicMock(), False)]

    service = ProductSyncService(client, repo)
    stats = service.sync(sync_run_logger=MagicMock())

    assert stats.fetched == 2
    assert stats.created == 1
    assert stats.updated == 1
    assert stats.failed == 0


def test_sync_continues_after_error():
    client = _fake_client([{"id": 7, "name": "A"}, {"id": 8, "name": "B"}])
    repo = MagicMock()
    repo.upsert.side_effect = [Exception("boom"), (MagicMock(), True)]

    sync_run_logger = MagicMock()
    service = ProductSyncService(client, repo)
    stats = service.sync(sync_run_logger=sync_run_logger)

    assert stats.fetched == 2
    assert stats.created == 1
    assert stats.failed == 1
    sync_run_logger.log_error.assert_called_once_with("product", 7, "boom")
