from mappers.utils import extract_id


def test_extract_id_from_many2one_list():
    assert extract_id([42, "Some Name"]) == 42


def test_extract_id_returns_none_when_false():
    """وقتی رابطه Many2one خالی باشه، Odoo مقدار False برمی‌گردونه."""
    assert extract_id(False) is None


def test_extract_id_returns_value_as_is_when_plain_int():
    assert extract_id(7) == 7