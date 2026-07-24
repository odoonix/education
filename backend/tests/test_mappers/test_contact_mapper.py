from mappers.contact_mapper import map_contact


def test_map_contact_with_all_fields():
    raw = {"id": 42, "name": "Ali Rezaei", "email": "ali@test.com", "phone": "021", "mobile": "0912"}
    entity = map_contact(raw)

    assert entity.odoo_id == 42
    assert entity.name == "Ali Rezaei"
    assert entity.email == "ali@test.com"
    assert entity.phone == "021"
    assert entity.mobile == "0912"


def test_map_contact_with_missing_optional_fields():
    """وقتی Odoo فیلد email/phone رو نداره (False برمی‌گردونه)، باید None بشه."""
    raw = {"id": 43, "name": "Sara Ahmadi", "email": False, "phone": False, "mobile": False}
    entity = map_contact(raw)

    assert entity.email is None
    assert entity.phone is None
    assert entity.mobile is None