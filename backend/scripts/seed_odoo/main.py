import logging
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.odoo_client.client import OdooClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("seed")


CONTACTS = [
    {"name": "علی رضایی", "email": "ali.rezaei@example.com", "phone": "021-1111111", "mobile": "0912-1111111"},
    {"name": "سارا محمدی", "email": "sara.mohammadi@example.com", "phone": "021-2222222", "mobile": "0912-2222222"},
    {"name": "حسین کریمی", "email": "hossein.karimi@example.com", "phone": "021-3333333", "mobile": "0912-3333333"},
]

PRODUCTS = [
    {"name": "لپ‌تاپ مدل A", "default_code": "SKU-A100", "list_price": 25000000, "type": "consu"},
    {"name": "موس بی‌سیم", "default_code": "SKU-M200", "list_price": 850000, "type": "consu"},
    {"name": "کیبورد مکانیکال", "default_code": "SKU-K300", "list_price": 2200000, "type": "consu"},
]


SALE_ORDERS = [
    {"customer_email": "ali.rezaei@example.com", "lines": [("SKU-A100", 1), ("SKU-M200", 2)]},
    {"customer_email": "sara.mohammadi@example.com", "lines": [("SKU-K300", 1)]},
    {"customer_email": "hossein.karimi@example.com", "lines": [("SKU-A100", 2), ("SKU-K300", 1), ("SKU-M200", 1)]},
]


def get_client() -> OdooClient:
    client = OdooClient(
        url=os.environ.get("ODOO_URL", "http://localhost:8069"),
        db=os.environ.get("ODOO_DB", "odoo"),
        username=os.environ.get("ODOO_USERNAME", "admin"),
        password=os.environ.get("ODOO_PASSWORD", "admin"),
    )
    client.authenticate()
    return client


def seed_contacts(client: OdooClient) -> dict[str, int]:
    email_to_id: dict[str, int] = {}
    for contact in CONTACTS:
        existing = client.search_read(
            "res.partner", [("email", "=", contact["email"])], ["id"], limit=1
        )
        if existing:
            logger.info("Contact %s already exists (id=%s)", contact["email"], existing[0]["id"])
            email_to_id[contact["email"]] = existing[0]["id"]
            continue
        new_id = client.create("res.partner", contact)
        logger.info("Contact %s created (id=%s)", contact["email"], new_id)
        email_to_id[contact["email"]] = new_id
    return email_to_id


def seed_products(client: OdooClient) -> dict[str, int]:
    code_to_id: dict[str, int] = {}
    for product in PRODUCTS:
        existing = client.search_read(
            "product.product",
            [("default_code", "=", product["default_code"])],
            ["id"],
            limit=1,
        )
        if existing:
            logger.info(
            "Product %s already exists (id=%s)", product["default_code"], existing[0]["id"]
        )
            code_to_id[product["default_code"]] = existing[0]["id"]
            continue
        new_id = client.create("product.product", product)
        logger.info("Product %s created (id=%s)", product["default_code"], new_id)
        code_to_id[product["default_code"]] = new_id
    return code_to_id


def seed_sale_orders(
    client: OdooClient, email_to_id: dict[str, int], code_to_id: dict[str, int]
) -> None:
    for order in SALE_ORDERS:
        partner_id = email_to_id[order["customer_email"]]
        existing_orders = client.search_read(
            "sale.order", [("partner_id", "=", partner_id)], ["id"]
        )
        if existing_orders:
            logger.info(
                "Order already exists for customer with partner_id=%s; skipped", partner_id
            )
            continue

        order_lines = [
            (0, 0, {"product_id": code_to_id[code], "product_uom_qty": qty})
            for code, qty in order["lines"]
        ]
        order_id = client.create(
            "sale.order",
            {"partner_id": partner_id, "order_line": order_lines},
        )
        logger.info("Order created (id=%s, partner_id=%s)", order_id, partner_id)


def main() -> None:
    client = get_client()
    logger.info("Starting seeding of Odoo data...")
    email_to_id = seed_contacts(client)
    code_to_id = seed_products(client)
    seed_sale_orders(client, email_to_id, code_to_id)
    logger.info("Seeding of Odoo data ended.")


if __name__ == "__main__":
    main()
