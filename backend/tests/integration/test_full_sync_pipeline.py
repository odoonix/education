"""
Integration Test: Run the entire pipeline through actual run_full_sync
(not by calling each service manually), with a fake OdooClient and a real PostgreSQL
database (the same database used in docker-compose).

This test follows exactly the same path as in production:
SyncOrchestrator -> Repositories -> Services -> DB, only the network layer to
Odoo is mocked. The goal is to verify the correct interaction between layers,
not just the behavior of each one in isolation (which is covered in unit tests).

The most important scenario: **running the entire sync twice should not create duplicate data**
(idempotency at the whole-system level, not just a single Repository).
"""
import pytest

from app.db.models import Contact, Product, SaleOrder, SaleOrderLine, SyncLog, SyncRun
from app.services.sync_orchestrator import run_full_sync

pytestmark = pytest.mark.integration


ODOO_DATA = {
    "res.partner": [
        {"id": 1, "name": "Ali", "email": "ali@x.com", "phone": "111", "mobile": "999"},
        {"id": 2, "name": "Sara", "email": "sara@x.com", "phone": "222", "mobile": "888"},
    ],
    "product.product": [
        {"id": 10, "name": "Laptop", "default_code": "SKU-A", "list_price": 1000, "type": "consu"},
        {"id": 11, "name": "Mouse", "default_code": "SKU-B", "list_price": 50, "type": "consu"},
    ],
    "sale.order": [
        {"id": 100, "name": "S00001", "partner_id": [1, "Ali"], "date_order": "2026-07-01", "state": "sale", "amount_total": 2050},
        {"id": 101, "name": "S00002", "partner_id": [999, "Ghost"], "date_order": "2026-07-02", "state": "draft", "amount_total": 50},
    ],
    "sale.order.line": [
        {"id": 1000, "order_id": [100, "S00001"], "product_id": [10, "Laptop"], "product_uom_qty": 2, "price_unit": 1000, "price_subtotal": 2000},
        {"id": 1001, "order_id": [100, "S00001"], "product_id": [11, "Mouse"], "product_uom_qty": 1, "price_unit": 50, "price_subtotal": 50},
        {"id": 1002, "order_id": [999, "Missing"], "product_id": [10, "Laptop"], "product_uom_qty": 1, "price_unit": 1, "price_subtotal": 1},
    ],
}


def _fake_odoo_client():
    from unittest.mock import MagicMock

    client = MagicMock()

    def _iter_all(model, domain, fields, batch_size=100):
        return iter(ODOO_DATA.get(model, []))

    client.iter_all.side_effect = _iter_all
    return client


class TestFullSyncPipeline:
    def test_first_run_creates_everything_correctly(self, pg_session_factory):
        stats = run_full_sync(
            odoo_client=_fake_odoo_client(), session_factory=pg_session_factory
        )

        assert stats["fetched"] == 9
        assert stats["failed"] == 1

        session = pg_session_factory()
        try:
            assert session.query(Contact).count() == 2
            assert session.query(Product).count() == 2
            assert session.query(SaleOrder).count() == 2
            assert session.query(SaleOrderLine).count() == 2

            sync_run = session.query(SyncRun).one()
            assert sync_run.created_count == 8

            error_logs = session.query(SyncLog).filter_by(level="error").all()
            assert len(error_logs) == 1

            warning_logs = session.query(SyncLog).filter_by(level="warning").all()
            assert len(warning_logs) == 1
        finally:
            session.close()

    def test_second_run_does_not_duplicate_anything(self, pg_session_factory):
        run_full_sync(odoo_client=_fake_odoo_client(), session_factory=pg_session_factory)
        stats_second_run = run_full_sync(
            odoo_client=_fake_odoo_client(), session_factory=pg_session_factory
        )

        assert stats_second_run["created"] == 0
        assert stats_second_run["updated"] == 8
        assert stats_second_run["failed"] == 1

        session = pg_session_factory()
        try:
            assert session.query(Contact).count() == 2
            assert session.query(Product).count() == 2
            assert session.query(SaleOrder).count() == 2
            assert session.query(SaleOrderLine).count() == 2

            assert session.query(SyncRun).count() == 2
        finally:
            session.close()

    def test_updated_data_from_odoo_is_reflected_on_second_run(self, pg_session_factory):
        run_full_sync(odoo_client=_fake_odoo_client(), session_factory=pg_session_factory)

        updated_data = {
            **ODOO_DATA,
            "product.product": [
                {"id": 10, "name": "Laptop Pro", "default_code": "SKU-A", "list_price": 1500, "type": "consu"},
                ODOO_DATA["product.product"][1],
            ],
        }
        from unittest.mock import MagicMock

        client = MagicMock()
        client.iter_all.side_effect = lambda model, domain, fields, batch_size=100: iter(
            updated_data.get(model, [])
        )

        run_full_sync(odoo_client=client, session_factory=pg_session_factory)

        session = pg_session_factory()
        try:
            product = session.query(Product).filter_by(odoo_id=10).one()
            assert product.name == "Laptop Pro"
            assert float(product.sale_price) == 1500
            assert session.query(Product).filter_by(odoo_id=10).count() == 1
        finally:
            session.close()
