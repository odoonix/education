from datetime import datetime, timezone

import pytest

from backend.adapters.base import ErpAdapter
from backend.adapters.odoo_adapter import OdooConnectionError
from backend.services.sync_service import SyncService


class FakeOdooAdapter(ErpAdapter):
    def __init__(self, contacts=None, products=None, orders=None, order_lines=None, fail_contacts_once=False):
        self._contacts = contacts or []
        self._products = products or []
        self._orders = orders or []
        self._order_lines = order_lines or []
        self._fail_contacts_once = fail_contacts_once
        self._contacts_call_count = 0

    def fetch_contacts(self, offset=0, limit=100, since=None):
        self._contacts_call_count += 1
        if self._fail_contacts_once and self._contacts_call_count == 1:
            raise OdooConnectionError("simulated transient failure")
        return self._contacts[offset:offset + limit]

    def fetch_products(self, offset=0, limit=100, since=None):
        return self._products[offset:offset + limit]

    def fetch_sale_orders(self, offset=0, limit=100, since=None):
        return self._orders[offset:offset + limit]

    def fetch_sale_order_lines(self, order_ids):
        return [line for line in self._order_lines if line["order_id"][0] in order_ids]


@pytest.fixture
def contact_raw():
    return {"id": 1, "name": "Ali", "email": "ali@example.com", "phone": None, "mobile": None}


@pytest.fixture
def product_raw():
    return {"id": 10, "name": "Mouse", "default_code": "PRD-001", "list_price": 15.5, "type": "consu"}


@pytest.fixture
def order_raw():
    return {
        "id": 1000, "name": "S00001", "partner_id": [1, "Ali"],
        "date_order": "2026-01-15 10:00:00", "state": "sale", "amount_total": 31.0,
    }


@pytest.fixture
def line_raw():
    return {
        "id": 100, "order_id": [1000, "S00001"], "product_id": [10, "Mouse"],
        "product_uom_qty": 2.0, "price_unit": 15.5, "price_subtotal": 31.0,
    }


def test_full_sync_creates_all_records(session, contact_raw, product_raw, order_raw, line_raw):
    odoo = FakeOdooAdapter(contacts=[contact_raw], products=[product_raw], orders=[order_raw], order_lines=[line_raw])
    service = SyncService(session, odoo)

    run = service.run_full_sync()

    assert run.fetched_count == 3
    assert run.created_count == 3
    assert run.error_count == 0


def test_full_sync_is_idempotent_on_second_run(session, contact_raw, product_raw, order_raw, line_raw):
    odoo = FakeOdooAdapter(contacts=[contact_raw], products=[product_raw], orders=[order_raw], order_lines=[line_raw])
    service = SyncService(session, odoo)

    service.run_full_sync()
    second_run = service.run_full_sync()

    assert second_run.created_count == 0
    assert second_run.updated_count == 3
    assert second_run.error_count == 0


def test_sale_order_with_missing_customer_is_isolated_as_error(session, product_raw, order_raw, line_raw):
    odoo = FakeOdooAdapter(contacts=[], products=[product_raw], orders=[order_raw], order_lines=[line_raw])
    service = SyncService(session, odoo)

    run = service.run_full_sync()

    assert run.error_count == 1
    assert run.fetched_count == 2
    assert len(run.logs) == 1
    assert run.logs[0].record_odoo_id == 1000


def test_transient_odoo_failure_is_retried_and_recovers(session, contact_raw, product_raw, order_raw, line_raw):
    odoo = FakeOdooAdapter(
        contacts=[contact_raw], products=[product_raw], orders=[order_raw],
        order_lines=[line_raw], fail_contacts_once=True,
    )
    service = SyncService(session, odoo)

    run = service.run_full_sync()

    assert run.error_count == 0
    assert run.created_count == 3