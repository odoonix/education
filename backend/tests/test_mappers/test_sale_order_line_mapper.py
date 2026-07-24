from mappers.sale_order_line_mapper import map_sale_order_line


def test_map_sale_order_line_extracts_both_many2one_fields():
    raw = {
        "id": 200,
        "order_id": [100, "S00100"],
        "product_id": [77, "[REF-77] Some Product"],
        "product_uom_qty": 3.0,
        "price_unit": 25.0,
        "price_subtotal": 75.0,
    }
    entity = map_sale_order_line(raw)

    assert entity.sale_order_odoo_id == 100
    assert entity.product_odoo_id == 77
    assert entity.quantity == 3.0
    assert entity.subtotal == 75.0