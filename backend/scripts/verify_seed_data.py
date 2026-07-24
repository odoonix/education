
import os
import xmlrpc.client

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")


def get_connection():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise RuntimeError("Authentication failed.")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def call(models, uid, model, method, *args, **kwargs):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, list(args), kwargs)


def show(title, model, fields, domain=None, limit=3):
    print(f"\n=== {title} ===")
    domain = domain or []
    count = call(models, uid, model, "search_count", domain)
    print(f"Total records: {count}")

    sample = call(models, uid, model, "search_read", domain, fields=fields, limit=limit)
    for row in sample:
        print(row)


uid, models = get_connection()

show(
    "Contacts (res.partner)",
    "res.partner",
    ["id", "name", "email", "phone", "mobile"],
)

show(
    "Products (product.template)",
    "product.template",
    ["id", "name", "default_code", "list_price", "type"],
)

show(
    "Sale Orders (sale.order)",
    "sale.order",
    ["id", "name", "partner_id", "date_order", "state", "amount_total"],
    domain=[["client_order_ref", "like", "SEED-"]],
)

show(
    "Sale Order Lines (sale.order.line)",
    "sale.order.line",
    ["id", "order_id", "product_id", "product_uom_qty", "price_unit", "price_subtotal"],
)

print("\n=== Sanity check ===")
draft_count = call(models, uid, "sale.order", "search_count", [["state", "=", "draft"]])
sale_count = call(models, uid, "sale.order", "search_count", [["state", "=", "sale"]])
print(f"Orders in state 'draft': {draft_count}")
print(f"Orders in state 'sale' (confirmed): {sale_count}")