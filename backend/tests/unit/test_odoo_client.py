"""
Tests for OdooClient by mocking xmlrpc.client.ServerProxy.
No real network is involved here; only authentication behavior, errors, retry, and
pagination (iter_all) are tested.
"""
import xmlrpc.client
from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import OdooConnectionError
from app.odoo_client.client import OdooClient


@pytest.fixture()
def client_with_mocked_proxies(monkeypatch):
    common_proxy = MagicMock()
    models_proxy = MagicMock()

    def fake_server_proxy(url, allow_none=True):  # noqa: ARG001
        return common_proxy if url.endswith("/xmlrpc/2/common") else models_proxy

    with patch("xmlrpc.client.ServerProxy", side_effect=fake_server_proxy):
        client = OdooClient(
            url="http://fake-odoo:8069", db="testdb", username="admin", password="admin"
        )
    return client, common_proxy, models_proxy


class TestAuthenticate:
    def test_authenticate_success_sets_uid(self, client_with_mocked_proxies):
        client, common_proxy, _ = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 7

        uid = client.authenticate()

        assert uid == 7
        assert client.uid == 7
        common_proxy.authenticate.assert_called_once_with("testdb", "admin", "admin", {})

    def test_authenticate_rejected_raises_connection_error(self, client_with_mocked_proxies):
        client, common_proxy, _ = client_with_mocked_proxies
        common_proxy.authenticate.return_value = False  # Odoo این را برای رد شدن برمی‌گرداند

        with pytest.raises(OdooConnectionError):
            client.authenticate()

    def test_uid_property_authenticates_lazily(self, client_with_mocked_proxies):
        client, common_proxy, _ = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 3

        assert client._uid is None
        assert client.uid == 3  # اولین دسترسی باید authenticate را صدا بزند
        assert common_proxy.authenticate.call_count == 1

        _ = client.uid  # دسترسی دوم نباید دوباره authenticate کند
        assert common_proxy.authenticate.call_count == 1


class TestSearchReadAndExecuteKw:
    def test_search_read_calls_execute_kw_with_correct_args(self, client_with_mocked_proxies):
        client, common_proxy, models_proxy = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 1
        models_proxy.execute_kw.return_value = [{"id": 1, "name": "Ali"}]

        result = client.search_read(
            "res.partner", domain=[("email", "!=", False)], fields=["id", "name"],
            offset=10, limit=50,
        )

        assert result == [{"id": 1, "name": "Ali"}]
        models_proxy.execute_kw.assert_called_once_with(
            "testdb", 1, "admin",
            "res.partner", "search_read",
            [[("email", "!=", False)], ["id", "name"]],
            {"offset": 10, "limit": 50},
        )

    def test_execute_kw_wraps_unexpected_errors(self, client_with_mocked_proxies):
        client, common_proxy, models_proxy = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 1
        models_proxy.execute_kw.side_effect = ValueError("weird odoo error")

        with pytest.raises(OdooConnectionError):
            client.search_read("res.partner", [], ["id"])

    def test_execute_kw_retries_on_protocol_error(self, client_with_mocked_proxies, monkeypatch):
        client, common_proxy, models_proxy = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 1
        monkeypatch.setattr("app.retry.time.sleep", lambda s: None)

        models_proxy.execute_kw.side_effect = [
            xmlrpc.client.ProtocolError("http://x", 500, "err", {}),
            [{"id": 1}],
        ]

        result = client.search_read("res.partner", [], ["id"])
        assert result == [{"id": 1}]
        assert models_proxy.execute_kw.call_count == 2


class TestIterAll:
    def test_iter_all_paginates_until_short_batch(self, client_with_mocked_proxies):
        client, common_proxy, models_proxy = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 1

        page1 = [{"id": i} for i in range(1, 3)] 
        page2 = [{"id": 3}] 
        models_proxy.execute_kw.side_effect = [page1, page2]

        rows = list(client.iter_all("res.partner", [], ["id"], batch_size=2))

        assert [r["id"] for r in rows] == [1, 2, 3]
        assert models_proxy.execute_kw.call_count == 2

    def test_iter_all_stops_immediately_on_empty_result(self, client_with_mocked_proxies):
        client, common_proxy, models_proxy = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 1
        models_proxy.execute_kw.return_value = []

        rows = list(client.iter_all("res.partner", [], ["id"], batch_size=100))

        assert rows == []
        assert models_proxy.execute_kw.call_count == 1


class TestCreate:
    def test_create_returns_new_id(self, client_with_mocked_proxies):
        client, common_proxy, models_proxy = client_with_mocked_proxies
        common_proxy.authenticate.return_value = 1
        models_proxy.execute_kw.return_value = 42

        new_id = client.create("res.partner", {"name": "Ali"})

        assert new_id == 42
        models_proxy.execute_kw.assert_called_once_with(
            "testdb", 1, "admin", "res.partner", "create", [{"name": "Ali"}], {}
        )
