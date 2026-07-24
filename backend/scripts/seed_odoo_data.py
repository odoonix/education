
import os
import xmlrpc.client
from faker import Faker

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

NUM_CONTACTS = int(os.getenv("NUM_CONTACTS", 10_000))
NUM_PRODUCTS = int(os.getenv("NUM_PRODUCTS", 30_000))
NUM_SALE_ORDERS = int(os.getenv("NUM_SALE_ORDERS", 20_000))

CHUNK_SIZE = 1000
SO_CHUNK_SIZE = 100

BULK_CONTEXT = {
    "tracking_disable": True,
    "mail_create_nolog": True,
    "mail_notrack": True,
}

fake = Faker()


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


def create_contacts(uid, models):
    print(f"--- Creating {NUM_CONTACTS} contacts ---")


    existing = call(models, uid, "res.partner", "search_read", [], fields=["email"])
    existing_emails = {r["email"] for r in existing if r.get("email")}

    to_create = []
    seen_in_batch = set()
    while len(to_create) < NUM_CONTACTS:
        email = fake.unique.email()
        if email in existing_emails or email in seen_in_batch:
            continue
        seen_in_batch.add(email)
        to_create.append({
            "name": fake.name(),
            "email": email,
            "phone": fake.phone_number(),
            "mobile": fake.phone_number(),
        })

    created_ids = []
    for batch in chunked(to_create, CHUNK_SIZE):
        ids = call(models, uid, "res.partner", "create", batch)
        created_ids.extend(ids)
        print(f"  created {len(created_ids)}/{len(to_create)} contacts...")

    print(f"Done. {len(created_ids)} new contacts created "
          f"({len(existing_emails)} already existed before).")
    return created_ids


def create_products(uid, models):
    print(f"--- Creating {NUM_PRODUCTS} products ---")

    existing = call(models, uid, "product.template", "search_read", [], fields=["default_code"])
    existing_refs = {r["default_code"] for r in existing if r.get("default_code")}

    to_create = []
    for i in range(NUM_PRODUCTS):
        ref = f"PROD-{i + 1:05d}"
        if ref in existing_refs:
            continue
        to_create.append({
            "name": fake.unique.catch_phrase(),
            "default_code": ref,
            "list_price": round(fake.random_number(digits=4) / 100, 2),
            "type": "consu",
        })

    created_ids = []
    for batch in chunked(to_create, CHUNK_SIZE):
        ids = call(models, uid, "product.template", "create", batch)
        created_ids.extend(ids)
        print(f"  created {len(created_ids)}/{len(to_create)} products...")

    print(f"Done. {len(created_ids)} new products created.")
    return created_ids


def main():
    uid, models = get_connection()
    create_contacts(uid, models)
    create_products(uid, models)
    create_sale_orders(uid, models)

if __name__ == "__main__":
    main()