"""
Live Test: The only test in this project that requires a real Odoo instance.

It is SKIPPED by default because in typical CI environments and most local runs
(without docker compose up), no Odoo is available. To actually run it:

    docker compose up -d          # Bring up Odoo
    cd backend
    RUN_LIVE_ODOO_TESTS=1 ODOO_URL=http://localhost:8069 \
        ODOO_DB=sync_test pytest tests/live -m live -v

The purpose of this test is only to ensure the real XML-RPC path is correct (authentication
and a simple search_read) - not to repeat the sync logic which is already covered
by integration tests with mocks.
"""
import os

import pytest

from app.config import settings
from app.odoo_client.client import OdooClient

pytestmark = pytest.mark.live

RUN_LIVE = os.environ.get("RUN_LIVE_ODOO_TESTS") == "1"

skip_reason = (
    "This test only runs with a real Odoo instance. To enable: "
    "docker compose up -d and then RUN_LIVE_ODOO_TESTS=1 pytest tests/live -m live"
)

@pytest.mark.skipif(not RUN_LIVE, reason=skip_reason)
class TestLiveOdooConnection:
    def test_authenticate_succeeds(self):
        client = OdooClient(
            url=settings.odoo_url,
            db=settings.odoo_db,
            username=settings.odoo_username,
            password=settings.odoo_password,
        )
        uid = client.authenticate()
        assert isinstance(uid, int)
        assert uid > 0

    def test_search_read_contacts(self):
        client = OdooClient(
            url=settings.odoo_url,
            db=settings.odoo_db,
            username=settings.odoo_username,
            password=settings.odoo_password,
        )
        client.authenticate()
        rows = client.search_read(
            "res.partner", domain=[], fields=["id", "name"], limit=5
        )
        assert isinstance(rows, list)

    def test_pagination_returns_all_records_without_duplicates(self):
        client = OdooClient(
            url=settings.odoo_url,
            db=settings.odoo_db,
            username=settings.odoo_username,
            password=settings.odoo_password,
        )
        client.authenticate()
        seen_ids = set()
        for row in client.iter_all("res.partner", [], ["id"], batch_size=2):
            assert row["id"] not in seen_ids, "iter_all باید هر رکورد را فقط یک‌بار برگرداند"
            seen_ids.add(row["id"])
        assert len(seen_ids) > 0
