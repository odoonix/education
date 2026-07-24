from adapters.odoo_adapter import OdooAdapter


def test_get_contacts_calls_correct_odoo_method(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")

    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 42

    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = [
        {"id": 1, "name": "Test Contact", "email": "t@test.com", "phone": None, "mobile": None}
    ]

    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter(url="http://fake-odoo", db="testdb", username="user", password="pass")
    result = adapter.get_contacts(limit=10)

    assert result == [{"id": 1, "name": "Test Contact", "email": "t@test.com", "phone": None, "mobile": None}]

    mock_common.authenticate.assert_called_once_with("testdb", "user", "pass", {})
    mock_models.execute_kw.assert_called_once_with(
        "testdb", 42, "pass", "res.partner", "search_read", [[]],
        {"fields": ["id", "name", "email", "phone", "mobile"], "offset": 0, "limit": 10},
    )


def test_authentication_failure_raises_connection_error(mocker):
    from core.exceptions import OdooAuthenticationError
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")

    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = False

    mock_server_proxy.return_value = mock_common

    adapter = OdooAdapter(url="http://fake-odoo", db="testdb", username="wrong", password="wrong")

    import pytest
    with pytest.raises(OdooAuthenticationError, match="Odoo authentication failed"):
        adapter.count_contacts()


def test_connection_is_lazy_and_cached(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")

    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 42

    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = 5

    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter(url="http://fake-odoo", db="testdb", username="user", password="pass")
    adapter.count_contacts()
    adapter.count_products()

    mock_common.authenticate.assert_called_once()



def test_get_products_calls_correct_odoo_method(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")
    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 1
    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = [{"id": 1, "name": "P", "default_code": "X", "list_price": 5.0, "type": "consu"}]
    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter("http://fake", "db", "u", "p")
    result = adapter.get_products(limit=5)

    assert len(result) == 1
    mock_models.execute_kw.assert_called_once_with(
        "db", 1, "p", "product.template", "search_read", [[]],
        {"fields": ["id", "name", "default_code", "list_price", "type"], "offset": 0, "limit": 5},
    )


def test_count_products(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")
    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 1
    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = 42
    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter("http://fake", "db", "u", "p")
    assert adapter.count_products() == 42


def test_get_sale_orders_calls_correct_odoo_method(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")
    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 1
    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = [{"id": 1, "name": "S1"}]
    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter("http://fake", "db", "u", "p")
    result = adapter.get_sale_orders(limit=5)
    assert len(result) == 1


def test_count_sale_orders(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")
    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 1
    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = 7
    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter("http://fake", "db", "u", "p")
    assert adapter.count_sale_orders() == 7


def test_get_sale_order_lines_calls_correct_odoo_method(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")
    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 1
    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = [{"id": 1}]
    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter("http://fake", "db", "u", "p")
    result = adapter.get_sale_order_lines(limit=5)
    assert len(result) == 1


def test_count_sale_order_lines(mocker):
    mock_server_proxy = mocker.patch("adapters.odoo_adapter.xmlrpc.client.ServerProxy")
    mock_common = mocker.Mock()
    mock_common.authenticate.return_value = 1
    mock_models = mocker.Mock()
    mock_models.execute_kw.return_value = 9
    mock_server_proxy.side_effect = [mock_common, mock_models]

    adapter = OdooAdapter("http://fake", "db", "u", "p")
    assert adapter.count_sale_order_lines() == 9