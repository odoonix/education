
import os
import random
import xmlrpc.client
from datetime import datetime, timedelta

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

NUM_SALE_ORDERS = int(os.getenv("NUM_SALE_ORDERS", 20_000))
SO_CHUNK_SIZE = 100

BULK_CONTEXT = {
    "tracking_disable": True,
    "mail_create_nolog": True,
    "mail_notrack": True,
}


def get_connection():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise RuntimeError("Authentication failed.")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def call(models, uid, model, method, *args, context=None, **kwargs):
    if context is not None:
        kwargs["context"] = context
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, list(args), kwargs)


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def create_sale_orders(uid, models):
    print(f"--- Creating {NUM_SALE_ORDERS} sale orders ---")

    partner_ids = [r["id"] for r in call(models, uid, "res.partner", "search_read", [], fields=["id"])]
    products = call(models, uid, "product.product", "search_read", [], fields=["id", "list_price"])

    print(f"Found {len(partner_ids)} contacts and {len(products)} products to use.")

    if not partner_ids or not products:
        raise RuntimeError("No contacts/products found in Odoo. Create them first.")

    existing = call(
        models, uid, "sale.order", "search_read",
        [["client_order_ref", "like", "SEED-"]],
        fields=["client_order_ref"],
    )
    existing_refs = {r["client_order_ref"] for r in existing}
    print(f"{len(existing_refs)} seed sale orders already exist, will skip those.")

    to_create = []
    for i in range(NUM_SALE_ORDERS):
        ref = f"SEED-{i + 1:06d}"
        if ref in existing_refs:
            continue

        num_lines = random.randint(1, 3)
        chosen_products = random.sample(products, k=min(num_lines, len(products)))
        order_lines = []
        for p in chosen_products:
            qty = random.randint(1, 10)
            order_lines.append((0, 0, {
                "product_id": p["id"],
                "product_uom_qty": qty,
                "price_unit": p["list_price"],
            }))

        order_date = datetime.now() - timedelta(days=random.randint(0, 365))
        to_create.append({
            "partner_id": random.choice(partner_ids),
            "client_order_ref": ref,
            "date_order": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "order_line": order_lines,
        })

    print(f"{len(to_create)} new sale orders to create.")

    created_ids = []
    for batch in chunked(to_create, SO_CHUNK_SIZE):
        ids = call(models, uid, "sale.order", "create", batch, context=BULK_CONTEXT)
        created_ids.extend(ids)
        print(f"  created {len(created_ids)}/{len(to_create)} sale orders...")

    print(f"Done. {len(created_ids)} new sale orders created "
          f"({len(existing_refs)} already existed before).")

    confirm_count = min(len(created_ids), max(1, len(created_ids) // 2))
    to_confirm = random.sample(created_ids, k=confirm_count) if created_ids else []
    for batch in chunked(to_confirm, SO_CHUNK_SIZE):
        call(models, uid, "sale.order", "action_confirm", batch)
    print(f"Confirmed {confirm_count} sale orders (state -> 'sale').")

    return created_ids


def main():
    uid, models = get_connection()
    create_sale_orders(uid, models)


if __name__ == "__main__":
    main()