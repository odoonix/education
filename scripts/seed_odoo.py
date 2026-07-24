"""Seed the Odoo instance with test data (idempotent).

Runs standalone and reads ODOO_* from the environment. Used by the
`odoo_seed` service so that `docker compose up` produces a populated
Odoo for the sync to read from. Safe to run repeatedly.
"""
import os
import time
import xmlrpc.client


ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB_NAME", "odoo_test")
ODOO_USER = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")


CONTACTS = [
    {"name": "Ali Ahmadi", "email": "ali.ahmadi@test.com",
     "phone": "+98 21 8877 0001", "mobile": "+98 912 345 6789"},
    {"name": "Reza Karimi", "email": "reza@test.com",
     "phone": "+98 21 4411 2233", "mobile": "+98 912 333 4455"},
    {"name": "Sara Mohammadi", "email": "sara@test.com",
     "phone": "+98 71 3222 3344", "mobile": "+98 912 999 8877"},
    {"name": "TechVision Co", "email": "info@techvision.test",
     "phone": "+98 21 8877 6655", "mobile": "+98 912 123 4567"},
    {"name": "Pars Data Solutions", "email": "contact@parsdata.test",
     "phone": "+98 71 3222 1144", "mobile": "+98 912 555 6677"},
]

PRODUCTS = [
    {"name": "Laptop Dell XPS", "default_code": "LAP-001",
     "list_price": 2500.0, "type": "consu"},
    {"name": "Mechanical Keyboard", "default_code": "KEY-001",
     "list_price": 120.0, "type": "consu"},
    {"name": "Wireless Mouse", "default_code": "MOU-001",
     "list_price": 45.0, "type": "consu"},
    {"name": '27" Monitor', "default_code": "MON-001",
     "list_price": 320.0, "type": "consu"},
    {"name": "USB-C Dock", "default_code": "DOC-001",
     "list_price": 180.0, "type": "consu"},
]

# ref, customer email, [(product default_code, qty, unit_price), ...]
ORDERS = [
    {"ref": "SEED-1", "customer": "info@techvision.test",
     "lines": [("LAP-001", 2, 2500.0), ("MOU-001", 3, 45.0)]},
    {"ref": "SEED-2", "customer": "contact@parsdata.test",
     "lines": [("MON-001", 1, 320.0), ("KEY-001", 4, 120.0)]},
    {"ref": "SEED-3", "customer": "reza@test.com",
     "lines": [("DOC-001", 5, 180.0)]},
]


def wait_for_odoo(common, retries=60, delay=5):
    for attempt in range(1, retries + 1):
        try:
            common.version()
            print(f"Odoo reachable (attempt {attempt})")
            return
        except Exception as exc:
            print(f"Waiting for Odoo... ({attempt}/{retries}): {exc}")
            time.sleep(delay)
    raise RuntimeError("Odoo did not become reachable in time")


def main():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    wait_for_odoo(common)

    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise RuntimeError("Odoo authentication failed")

    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    def execute(model, method, *args):
        return models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD, model, method, list(args)
        )

    def get_or_create(model, domain, values):
        found = execute(model, "search", domain)
        if found:
            return found[0]
        return execute(model, "create", values)

    # Installing sale_management with --without-demo does not add the admin
    # user to the Sales group, so grant it before touching sale.order.
    sales_group = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "ir.model.data", "search_read",
        [[["name", "=", "group_sale_manager"],
          ["module", "in", ["sales_team", "sale"]]]],
        {"fields": ["res_id"], "limit": 1},
    )
    if sales_group:
        execute("res.users", "write",
                [uid], {"groups_id": [(4, sales_group[0]["res_id"])]})
        print("granted Sales group to admin")

    partner_ids = {}
    for c in CONTACTS:
        partner_ids[c["email"]] = get_or_create(
            "res.partner", [["email", "=", c["email"]]], c
        )
    print(f"contacts ready: {len(partner_ids)}")

    product_ids = {}
    for p in PRODUCTS:
        product_ids[p["default_code"]] = get_or_create(
            "product.product", [["default_code", "=", p["default_code"]]], p
        )
    print(f"products ready: {len(product_ids)}")

    created = 0
    for o in ORDERS:
        if execute("sale.order", "search",
                   [["client_order_ref", "=", o["ref"]]]):
            continue
        order_lines = [
            (0, 0, {
                "product_id": product_ids[code],
                "product_uom_qty": qty,
                "price_unit": price,
            })
            for code, qty, price in o["lines"]
        ]
        execute("sale.order", "create", {
            "partner_id": partner_ids[o["customer"]],
            "client_order_ref": o["ref"],
            "order_line": order_lines,
        })
        created += 1
    print(f"sale orders created this run: {created}")
    print("Seed complete.")


if __name__ == "__main__":
    main()
