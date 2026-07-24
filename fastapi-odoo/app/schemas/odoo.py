from typing import Any


def get_odoo_id(value: Any) -> int:
    if isinstance(value, list):
        return value[0]

    if isinstance(value, int):
        return value

    raise ValueError(
        f"Expected an Odoo relational value, got: {value!r}"
    )