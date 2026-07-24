import xmlrpc.client

ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo_test"
ODOO_USERNAME = "admin@example.com"
ODOO_PASSWORD = "admin"

common = xmlrpc.client.ServerProxy(
    f"{ODOO_URL}/xmlrpc/2/common"
)

uid = common.authenticate(
    ODOO_DB,
    ODOO_USERNAME,
    ODOO_PASSWORD,
    {},
)

print(f"Authenticated user ID: {uid}")

models = xmlrpc.client.ServerProxy(
    f"{ODOO_URL}/xmlrpc/2/object"
)

contacts = models.execute_kw(
    ODOO_DB,
    uid,
    ODOO_PASSWORD,
    "res.partner",
    "search_read",
    [[]],
    {
        "fields": [
            "id",
            "name",
            "email",
            "phone",
            "mobile",
        ],
    },
)

print("\nContacts:")

for contact in contacts:
    print(contact)

products = models.execute_kw(
    ODOO_DB,
    uid,
    ODOO_PASSWORD,
    "product.template",
    "search_read",
    [[]],
    {
        "fields": [
            "id",
            "name",
            "default_code",
            "list_price",
            "type",
        ],
    },
)

print("\nProducts:")

for product in products:
    print(product)

sale_orders = models.execute_kw(
    ODOO_DB,
    uid,
    ODOO_PASSWORD,
    "sale.order",
    "search_read",
    [[]],
    {
        "fields": [
            "id",
            "name",
            "partner_id",
            "date_order",
            "state",
            "amount_total",
            "order_line",
        ],
    },
)

print("\nSale Orders:")

for order in sale_orders:
    print(order)

order_lines = models.execute_kw(
    ODOO_DB,
    uid,
    ODOO_PASSWORD,
    "sale.order.line",
    "search_read",
    [[]],
    {
        "fields": [
            "id",
            "order_id",
            "product_id",
            "product_uom_qty",
            "price_unit",
            "price_subtotal",
        ],
    },
)

print("\nSale Order Lines:")

for line in order_lines:
    print(line)

product_variants = models.execute_kw(
    ODOO_DB,
    uid,
    ODOO_PASSWORD,
    "product.product",
    "search_read",
    [[]],
    {
        "fields": [
            "id",
            "product_tmpl_id",
            "name",
            "default_code",
            "lst_price",
        ],
    },
)
product_variants = models.execute_kw(
    ODOO_DB,
    uid,
    ODOO_PASSWORD,
    "product.product",
    "search_read",
    [[]],
    {
        "fields": [
            "id",
            "product_tmpl_id",
            "name",
            "default_code",
            "lst_price",
        ],
    },
)

print("\nProduct Variants:")

for product in product_variants:
    print(product)