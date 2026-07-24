import xmlrpc.client

ODOO_URL = "http://localhost:8069"
ODOO_DB = "exam_db"
ODOO_USER = "admin"
ODOO_PASSWORD = "admin"

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    raise SystemExit("Authentication failed, check ODOO_USER / ODOO_PASSWORD / ODOO_DB")

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def call(model, method, *args):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, list(args))


contacts_data = [
    {"name": "Ali Rezaei", "email": "ali.rezaei@example.com", "phone": "02112345678", "mobile": "09121234567"},
    {"name": "Sara Ahmadi", "email": "sara.ahmadi@example.com", "phone": "02187654321", "mobile": "09129876543"},
    {"name": "Reza Karimi", "email": "reza.karimi@example.com", "phone": "02155667788", "mobile": "09123344556"},
]

contact_ids = []
for c in contacts_data:
    existing = call("res.partner", "search", [["email", "=", c["email"]]])
    if existing:
        contact_ids.append(existing[0])
        continue
    new_id = call("res.partner", "create", c)
    contact_ids.append(new_id)

print(f"Contacts ready: {contact_ids}")

products_data = [
    {"name": "Wireless Mouse", "default_code": "PRD-001", "list_price": 15.5, "type": "consu"},
    {"name": "Mechanical Keyboard", "default_code": "PRD-002", "list_price": 45.0, "type": "consu"},
    {"name": "USB-C Hub", "default_code": "PRD-003", "list_price": 22.75, "type": "consu"},
]

product_ids = []
for p in products_data:
    existing = call("product.product", "search", [["default_code", "=", p["default_code"]]])
    if existing:
        product_ids.append(existing[0])
        continue
    new_id = call("product.product", "create", p)
    product_ids.append(new_id)

print(f"Products ready: {product_ids}")

orders_data = [
    {
        "partner_id": contact_ids[0],
        "order_line": [
            (0, 0, {"product_id": product_ids[0], "product_uom_qty": 2, "price_unit": 15.5}),
            (0, 0, {"product_id": product_ids[1], "product_uom_qty": 1, "price_unit": 45.0}),
        ],
    },
    {
        "partner_id": contact_ids[1],
        "order_line": [
            (0, 0, {"product_id": product_ids[2], "product_uom_qty": 3, "price_unit": 22.75}),
        ],
    },
    {
        "partner_id": contact_ids[2],
        "order_line": [
            (0, 0, {"product_id": product_ids[0], "product_uom_qty": 5, "price_unit": 15.5}),
            (0, 0, {"product_id": product_ids[2], "product_uom_qty": 2, "price_unit": 22.75}),
        ],
    },
]

order_ids = []
for o in orders_data:
    new_id = call("sale.order", "create", o)
    order_ids.append(new_id)
    call("sale.order", "action_confirm", [new_id])

print(f"Sale orders created and confirmed: {order_ids}")    