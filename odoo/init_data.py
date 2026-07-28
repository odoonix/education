"""
اسکریپت ساخت داده‌های تستی در Odoo (Contacts, Products, Sale Orders).

این اسکریپت idempotent هست: اگه دوباره اجراش کنی، رکوردهای تکراری نمی‌سازه
(چون قبل از ساخت هر رکورد، چک می‌کنه که با همون شناسه (مثلاً همون ایمیل یا
همون Internal Reference) قبلاً وجود داره یا نه).

اجرا:
    python odoo/init_data.py
"""

import os
import ssl
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

# ابتدا تلاش می‌کند .env.local را بخواند، اگر نبود به سراغ .env می‌رود
load_dotenv(".env.local") or load_dotenv(".env")

# # ---------- خواندن ساده‌ی فایل .env.local یا .env بدون نیاز به کتابخانه‌ی خارجی ----------
# def load_env(base_dir: str | Path = ".") -> None:
#     base_path = Path(base_dir)
#     # اولویت اول با .env.local، در غیر این صورت .env
#     env_file = base_path / ".env.local"
#     if not env_file.exists():
#         env_file = base_path / ".env"

#     if not env_file.exists():
#         return

#     for line in env_file.read_text(encoding="utf-8").splitlines():
#         line = line.strip()
#         if not line or line.startswith("#") or "=" not in line:
#             continue
#         key, value = line.split("=", 1)
#         # مقداردهی مستقیم تا مقادیر فایل حتماً روی os.environ اعمال شوند
#         os.environ[key.strip()] = value.strip()


# load_env()

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "my_odoo_project")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin@gmail.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "Mohamad@77")


class OdooConnection:
    """یک wrapper ساده روی XML-RPC برای اتصال و صدا زدن متدهای Odoo."""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None

    def connect(self):
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        if not self.uid:
            raise RuntimeError(
                "اتصال به Odoo ناموفق بود. یوزرنیم/پسورد یا اسم دیتابیس رو چک کن."
            )
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        print(f"[OK] به Odoo وصل شدیم. uid={self.uid}")
        return self

    def execute(self, model: str, method: str, *args, **kwargs):
        return self.models.execute_kw(
            self.db, self.uid, self.password, model, method, list(args), kwargs
        )

    def search(self, model: str, domain: list) -> list:
        return self.execute(model, "search", domain)

    def search_read(self, model: str, domain: list, fields: list) -> list:
        return self.execute(model, "search_read", domain, {"fields": fields})

    def create(self, model: str, values: dict) -> int:
        return self.execute(model, "create", values)

    def write(self, model: str, record_id: int, values: dict) -> bool:
        return self.execute(model, "write", [record_id], values)


def get_or_create_contact(conn: OdooConnection, data: dict) -> int:
    """اگه Contact با همین ایمیل وجود داشت همونو برمی‌گردونه، وگرنه می‌سازه."""
    existing = conn.search("res.partner", [["email", "=", data["email"]]])
    if existing:
        print(f"  - Contact '{data['name']}' از قبل هست (id={existing[0]}), رد شدیم.")
        return existing[0]
    contact_id = conn.create("res.partner", data)
    print(f"  + Contact '{data['name']}' ساخته شد (id={contact_id})")
    return contact_id


def get_or_create_product(conn: OdooConnection, data: dict) -> int:
    """اگه Product با همین Internal Reference (default_code) وجود داشت، همونو برمی‌گردونه."""
    existing = conn.search("product.product", [["default_code", "=", data["default_code"]]])
    if existing:
        print(f"  - Product '{data['name']}' از قبل هست (id={existing[0]}), رد شدیم.")
        return existing[0]
    product_id = conn.create("product.product", data)
    print(f"  + Product '{data['name']}' ساخته شد (id={product_id})")
    return product_id


def get_or_create_sale_order(conn: OdooConnection, partner_id: int, order_date: str,
                              lines: list, client_order_ref: str) -> int:
    """
    برای جلوگیری از تکرار، از client_order_ref (فیلد "Customer Reference")
    به عنوان شناسه‌ی یکتا استفاده می‌کنیم چون در این سناریو مصنوعیه و
    راحت می‌تونیم تشخیص بدیم قبلاً ساخته شده یا نه.
    """
    existing = conn.search("sale.order", [["client_order_ref", "=", client_order_ref]])
    if existing:
        print(f"  - Sale Order '{client_order_ref}' از قبل هست (id={existing[0]}), رد شدیم.")
        return existing[0]

    order_lines = [
        (0, 0, {
            "product_id": line["product_id"],
            "product_uom_qty": line["qty"],
            "price_unit": line["price_unit"],
        })
        for line in lines
    ]

    order_id = conn.create("sale.order", {
        "partner_id": partner_id,
        "date_order": order_date,
        "client_order_ref": client_order_ref,
        "order_line": order_lines,
    })
    print(f"  + Sale Order '{client_order_ref}' ساخته شد (id={order_id})")
    return order_id


def main():
    conn = OdooConnection(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD).connect()

    print("\n--- ساخت Contacts ---")
    contacts_data = [
        {"name": "Ali Rezaei", "email": "ali.rezaei@example.com", "phone": "+98 21 1111 1111", "mobile": "+98 912 111 1111"},
        {"name": "Sara Ahmadi", "email": "sara.ahmadi@example.com", "phone": "+98 21 2222 2222", "mobile": "+98 912 222 2222"},
        {"name": "Reza Karimi", "email": "reza.karimi@example.com", "phone": "+98 21 3333 3333", "mobile": "+98 912 333 3333"},
    ]
    contact_ids = [get_or_create_contact(conn, c) for c in contacts_data]

    print("\n--- ساخت Products ---")
    products_data = [
        {"name": "Wireless Mouse", "default_code": "PRD-001", "list_price": 25.0, "type": "consu"},
        {"name": "Mechanical Keyboard", "default_code": "PRD-002", "list_price": 75.0, "type": "consu"},
        {"name": "Consulting Service", "default_code": "PRD-003", "list_price": 100.0, "type": "service"},
    ]
    product_ids = [get_or_create_product(conn, p) for p in products_data]

    print("\n--- ساخت Sale Orders ---")
    get_or_create_sale_order(
        conn,
        partner_id=contact_ids[0],
        order_date="2026-06-01 10:00:00",
        client_order_ref="TEST-SO-001",
        lines=[
            {"product_id": product_ids[0], "qty": 2, "price_unit": 25.0},
            {"product_id": product_ids[1], "qty": 1, "price_unit": 75.0},
        ],
    )
    get_or_create_sale_order(
        conn,
        partner_id=contact_ids[1],
        order_date="2026-06-05 14:30:00",
        client_order_ref="TEST-SO-002",
        lines=[
            {"product_id": product_ids[2], "qty": 3, "price_unit": 100.0},
        ],
    )
    get_or_create_sale_order(
        conn,
        partner_id=contact_ids[2],
        order_date="2026-06-10 09:15:00",
        client_order_ref="TEST-SO-003",
        lines=[
            {"product_id": product_ids[0], "qty": 5, "price_unit": 25.0},
            {"product_id": product_ids[2], "qty": 1, "price_unit": 100.0},
        ],
    )

    print("\n[DONE] داده‌های تستی آماده‌ست.")


if __name__ == "__main__":
    main()