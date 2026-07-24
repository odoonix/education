import json
import xmlrpc.client
from pathlib import Path

from config import settings

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

common = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/common")

uid = common.authenticate(
    settings.ODOO_DATABASE,
    settings.ODOO_ADMIN_EMAIL,
    settings.ODOO_ADMIN_PASSWORD,
    {},
)

models = xmlrpc.client.ServerProxy(
    f"{settings.ODOO_URL}/xmlrpc/2/object"
)


def execute(model, method, *args, **kwargs):
    return models.execute_kw(
        settings.ODOO_DATABASE,
        uid,
        settings.ODOO_ADMIN_PASSWORD,
        model,
        method,
        list(args),
        kwargs,
    )


# --------------------------
# Contacts
# --------------------------

with open(DATA_DIR / "contacts.json", encoding="utf8") as f:    contacts = json.load(f)

partner_ids = {}

for contact in contacts:
    partner_id = execute(
        "res.partner",
        "create",
        contact,
    )

    partner_ids[contact["email"]] = partner_id

# --------------------------
# Products
# --------------------------

with open(DATA_DIR / "products.json", encoding="utf8") as f:
    products = json.load(f)

product_ids = {}

for product in products:
    template_id = execute(
        "product.template",
        "create",
        product,
    )

    template = execute(
        "product.template",
        "read",
        [template_id],
        fields=[
            "product_variant_id"
        ],
    )

    variant_id = template[0]["product_variant_id"][0]

    product_ids[
        product["default_code"]
    ] = variant_id
# --------------------------
# Sale Orders
# --------------------------

with open(DATA_DIR / "sale_orders.json", encoding="utf8") as f:
    orders = json.load(f)

for order in orders:

    sale_order_id = execute(
        "sale.order",
        "create",
        {
            "partner_id": partner_ids[
                order["customer_email"]
            ],
            "date_order": order["date_order"],
        },
    )

    for line in order["lines"]:
        execute(
            "sale.order.line",
            "create",
            {
                "order_id": sale_order_id,
                "product_id": product_ids[
                    line["product_code"]
                ],
                "product_uom_qty": line["quantity"],
                "price_unit": line["price_unit"],
            },
        )

print("Seed completed successfully.")
