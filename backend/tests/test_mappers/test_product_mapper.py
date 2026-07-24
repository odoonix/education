from mappers.product_mapper import map_product


def test_map_product_with_all_fields():
    raw = {"id": 5, "name": "Widget", "default_code": "W-001", "list_price": 19.99, "type": "consu"}
    entity = map_product(raw)

    assert entity.odoo_id == 5
    assert entity.name == "Widget"
    assert entity.default_code == "W-001"
    assert entity.list_price == 19.99
    assert entity.product_type == "consu"


def test_map_product_with_missing_default_code():
    raw = {"id": 6, "name": "No Code Product", "default_code": False, "list_price": 5.0, "type": "service"}
    entity = map_product(raw)

    assert entity.default_code is None