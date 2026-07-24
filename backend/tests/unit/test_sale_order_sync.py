"""
Unit tests for SaleOrderSyncService with full mocking (no real database).
Scenarios covered: FK found, FK not found (warning), parent order of a line not found (error + skip), and continued processing after an error.
For end-to-end tests with a real database, see tests/integration/test_full_sync_pipeline.py.
"""
from unittest.mock import MagicMock

from app.services.sale_order_sync import SaleOrderSyncService


def _fake_client(orders=None, lines=None):
    client = MagicMock()

    def iter_all(model, domain, fields, batch_size=100):
        if model == "sale.order":
            return iter(orders or [])
        if model == "sale.order.line":
            return iter(lines or [])
        return iter([])

    client.iter_all.side_effect = iter_all
    return client


def _mock_entity(internal_id):
    entity = MagicMock()
    entity.id = internal_id
    return entity


class TestOrderSyncing:
    def test_order_with_known_customer_resolves_fk(self):
        client = _fake_client(
            orders=[{"id": 100, "name": "S1", "partner_id": [3, "Ali"], "amount_total": 100}]
        )
        contact_repo = MagicMock()
        contact_repo.get_by_odoo_id.return_value = _mock_entity(1)
        order_repo = MagicMock()
        order_repo.upsert.return_value = (MagicMock(), True)
        line_repo = MagicMock()
        product_repo = MagicMock()

        service = SaleOrderSyncService(client, order_repo, line_repo, contact_repo, product_repo)
        sync_run_logger = MagicMock()
        stats = service.sync(sync_run_logger)

        assert stats.created == 1
        assert stats.failed == 0
        order_repo.upsert.assert_called_once()
        called_data = order_repo.upsert.call_args[0][1]
        assert called_data["customer_id"] == 1
        sync_run_logger.log_warning.assert_not_called()

    def test_order_with_unknown_customer_logs_warning_but_still_saves(self):
        client = _fake_client(
            orders=[{"id": 100, "name": "S1", "partner_id": [999, "Ghost"], "amount_total": 50}]
        )
        contact_repo = MagicMock()
        contact_repo.get_by_odoo_id.return_value = None  # مخاطب sync نشده
        order_repo = MagicMock()
        order_repo.upsert.return_value = (MagicMock(), True)
        line_repo = MagicMock()
        product_repo = MagicMock()

        service = SaleOrderSyncService(client, order_repo, line_repo, contact_repo, product_repo)
        sync_run_logger = MagicMock()
        stats = service.sync(sync_run_logger)

        assert stats.created == 1  # سفارش همچنان ذخیره می‌شود
        called_data = order_repo.upsert.call_args[0][1]
        assert called_data["customer_id"] is None
        sync_run_logger.log_warning.assert_called_once()

    def test_order_processing_continues_after_error(self):
        client = _fake_client(
            orders=[
                {"id": 100, "name": "S1", "amount_total": 1},
                {"id": 101, "name": "S2", "amount_total": 2},
            ]
        )
        contact_repo = MagicMock()
        contact_repo.get_by_odoo_id.return_value = None
        order_repo = MagicMock()
        order_repo.upsert.side_effect = [Exception("db error"), (MagicMock(), True)]
        line_repo = MagicMock()
        product_repo = MagicMock()

        service = SaleOrderSyncService(client, order_repo, line_repo, contact_repo, product_repo)
        sync_run_logger = MagicMock()
        stats = service.sync(sync_run_logger)

        assert stats.fetched == 2
        assert stats.failed == 1
        assert stats.created == 1
        sync_run_logger.log_error.assert_any_call("sale_order", 100, "db error")


class TestOrderLineSyncing:
    def test_line_with_missing_parent_order_is_skipped(self):
        client = _fake_client(
            lines=[{"id": 1000, "order_id": [999, "Missing"], "product_id": [7, "P"]}]
        )
        contact_repo = MagicMock()
        order_repo = MagicMock()
        order_repo.get_by_odoo_id.return_value = None 
        line_repo = MagicMock()
        product_repo = MagicMock()

        service = SaleOrderSyncService(client, order_repo, line_repo, contact_repo, product_repo)
        sync_run_logger = MagicMock()
        stats = service.sync(sync_run_logger)

        assert stats.failed == 1
        line_repo.upsert.assert_not_called()
        sync_run_logger.log_error.assert_called_once()
        assert sync_run_logger.log_error.call_args[0][0] == "sale_order_line"

    def test_line_with_missing_product_logs_warning_but_still_saves(self):
        client = _fake_client(
            lines=[{"id": 1000, "order_id": [100, "S1"], "product_id": [999, "Ghost"]}]
        )
        contact_repo = MagicMock()
        order_repo = MagicMock()
        order_repo.get_by_odoo_id.return_value = _mock_entity(1)
        product_repo = MagicMock()
        product_repo.get_by_odoo_id.return_value = None
        line_repo = MagicMock()
        line_repo.upsert.return_value = (MagicMock(), True)

        service = SaleOrderSyncService(client, order_repo, line_repo, contact_repo, product_repo)
        sync_run_logger = MagicMock()
        stats = service.sync(sync_run_logger)

        assert stats.created == 1
        called_data = line_repo.upsert.call_args[0][1]
        assert called_data["product_id"] is None
        sync_run_logger.log_warning.assert_called_once()

    def test_line_with_valid_order_and_product_resolves_both_fks(self):
        client = _fake_client(
            lines=[
                {
                    "id": 1000,
                    "order_id": [100, "S1"],
                    "product_id": [7, "Laptop"],
                    "product_uom_qty": 2,
                    "price_unit": 500,
                    "price_subtotal": 1000,
                }
            ]
        )
        contact_repo = MagicMock()
        order_repo = MagicMock()
        order_repo.get_by_odoo_id.return_value = _mock_entity(1)
        product_repo = MagicMock()
        product_repo.get_by_odoo_id.return_value = _mock_entity(2)
        line_repo = MagicMock()
        line_repo.upsert.return_value = (MagicMock(), True)

        service = SaleOrderSyncService(client, order_repo, line_repo, contact_repo, product_repo)
        stats = service.sync(sync_run_logger=MagicMock())

        assert stats.created == 1
        called_data = line_repo.upsert.call_args[0][1]
        assert called_data["sale_order_id"] == 1
        assert called_data["product_id"] == 2
