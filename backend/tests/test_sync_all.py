from sync_all import main


def test_sync_all_calls_services_in_order(mocker):
    mocker.patch("sync_all.configure_logging")
    mocker.patch("sync_all.get_settings")

    fake_session = mocker.Mock()
    fake_adapter = mocker.Mock()

    mocker.patch("sync_all.SessionLocal", return_value=fake_session)
    mocker.patch("sync_all.OdooAdapter", return_value=fake_adapter)

    contacts = mocker.patch(
        "sync_all.sync_contacts",
        return_value={"status": "success"},
    )

    products = mocker.patch(
        "sync_all.sync_products",
        return_value={"status": "success"},
    )

    orders = mocker.patch(
        "sync_all.sync_sale_orders",
        return_value={"status": "success"},
    )

    lines = mocker.patch(
        "sync_all.sync_sale_order_lines",
        return_value={"status": "success"},
    )

    main()

    contacts.assert_called_once()
    products.assert_called_once()
    orders.assert_called_once()
    lines.assert_called_once()

    fake_session.close.assert_called_once()


def test_sync_all_stops_after_first_service(mocker):
    mocker.patch("sync_all.configure_logging")
    mocker.patch("sync_all.get_settings")

    fake_session = mocker.Mock()
    fake_adapter = mocker.Mock()

    mocker.patch("sync_all.SessionLocal", return_value=fake_session)
    mocker.patch("sync_all.OdooAdapter", return_value=fake_adapter)

    def stop(*args, **kwargs):
        kwargs["shutdown_handler"]._shutdown_requested = True
        return {"status": "interrupted"}

    contacts = mocker.patch(
        "sync_all.sync_contacts",
        side_effect=stop,
    )

    products = mocker.patch("sync_all.sync_products")
    orders = mocker.patch("sync_all.sync_sale_orders")
    lines = mocker.patch("sync_all.sync_sale_order_lines")

    main()

    contacts.assert_called_once()

    products.assert_not_called()
    orders.assert_not_called()
    lines.assert_not_called()

    fake_session.close.assert_called_once()