"""
چون sync_contact_service/sync_product_service/... فقط Wrapper نازک دور SyncEngine هستن،
تستشون فقط چک می‌کنه که پارامترهای درست (adapter method درست، mapper درست، repo درست) پاس داده می‌شن.
"""
from services.sync_contact_service import sync_contacts
from services.sync_product_service import sync_products
from services.sync_sale_order_service import sync_sale_orders
from services.sync_sale_order_line_service import sync_sale_order_lines


def test_sync_contacts_wires_engine_correctly(db_session, mocker):
    mock_engine = mocker.patch("services.sync_contact_service.SyncEngine")
    mock_engine.return_value.run.return_value = {"status": "success"}

    fake_adapter = mocker.Mock()
    result = sync_contacts(db_session, fake_adapter)

    assert result == {"status": "success"}
    call_kwargs = mock_engine.call_args.kwargs
    assert call_kwargs["operation_type"] == "contacts_sync"
    assert call_kwargs["count_fn"] == fake_adapter.count_contacts
    assert call_kwargs["fetch_page_fn"] == fake_adapter.get_contacts


def test_sync_products_wires_engine_correctly(db_session, mocker):
    mock_engine = mocker.patch("services.sync_product_service.SyncEngine")
    mock_engine.return_value.run.return_value = {"status": "success"}

    fake_adapter = mocker.Mock()

    shutdown = object()
    sync_products(db_session, fake_adapter, shutdown_handler=shutdown)

    call_kwargs = mock_engine.call_args.kwargs

    assert call_kwargs["shutdown_handler"] is shutdown
    sync_products(db_session, fake_adapter)

    call_kwargs = mock_engine.call_args.kwargs
    assert call_kwargs["operation_type"] == "products_sync"


def test_sync_sale_orders_wires_engine_correctly(db_session, mocker):
    mock_engine = mocker.patch("services.sync_sale_order_service.SyncEngine")
    mock_engine.return_value.run.return_value = {"status": "success"}

    fake_adapter = mocker.Mock()
    shutdown = object()

    sync_sale_orders(
        db_session,
        fake_adapter,
        shutdown_handler=shutdown,
    )

    call_kwargs = mock_engine.call_args.kwargs

    assert call_kwargs["shutdown_handler"] is shutdown
    sync_sale_orders(db_session, fake_adapter)

    call_kwargs = mock_engine.call_args.kwargs
    assert call_kwargs["operation_type"] == "sale_orders_sync"


def test_sync_sale_order_lines_wires_engine_correctly(db_session, mocker):
    mock_engine = mocker.patch("services.sync_sale_order_line_service.SyncEngine")
    mock_engine.return_value.run.return_value = {"status": "success"}

    fake_adapter = mocker.Mock()
    shutdown = object()

    sync_sale_order_lines(
        db_session,
        fake_adapter,
        shutdown_handler=shutdown,
    )

    call_kwargs = mock_engine.call_args.kwargs

    assert call_kwargs["shutdown_handler"] is shutdown
    sync_sale_order_lines(db_session, fake_adapter)

    call_kwargs = mock_engine.call_args.kwargs
    assert call_kwargs["operation_type"] == "sale_order_lines_sync"