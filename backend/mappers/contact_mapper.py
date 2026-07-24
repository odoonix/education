from core.entities import ContactEntity


def map_contact(raw: dict) -> ContactEntity:
    return ContactEntity(
        odoo_id=raw["id"],
        name=raw["name"],
        email=raw.get("email") or None,
        phone=raw.get("phone") or None,
        mobile=raw.get("mobile") or None,
    )