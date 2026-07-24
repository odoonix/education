from mappers.sale_order_mapper import map_sale_order


def test_map_sale_order_extracts_partner_id_from_many2one():
    raw = {
        "id": 100,
        "name": "S00100",
        "partner_id": [55, "Some Customer Name"],
        "date_order": "2026-01-15 10:30:00",
        "state": "sale",
        "amount_total": 250.5,
    }
    entity = map_sale_order(raw)

    assert entity.odoo_id == 100
    assert entity.contact_odoo_id == 55
    assert entity.date_order.year == 2026
    assert entity.date_order.month == 1
    assert entity.amount_total == 250.5