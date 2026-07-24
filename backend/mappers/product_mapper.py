from core.entities import ProductEntity


def map_product(raw: dict) -> ProductEntity:
    return ProductEntity(
        odoo_id=raw["id"],
        name=raw["name"],
        default_code=raw.get("default_code") or None,
        list_price=raw["list_price"],
        product_type=raw["type"],
    )