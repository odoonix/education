"""
اسکریپت تست مرحله ۶: کل مسیر «Odoo -> Mapper -> Repository -> PostgreSQL» رو
یک‌بار کامل اجرا می‌کنه. این هنوز Service Layer رسمی نیست (اون مرحله‌ی بعده)،
فقط برای اینه که ببینیم Repositoryها درست کار می‌کنن.

نکته‌ی مهم برای تست Idempotency:
این اسکریپت رو ۲ بار پشت‌سرهم اجرا کن. بار اول باید همه‌چیز "created" بشه،
بار دوم باید همه‌چیز "updated" بشه (نه created) — یعنی رکورد تکراری ساخته نشد.

اجرا:
    python scripts/test_repository_sync.py
"""

import os
import sys
from pathlib import Path

# ۱. یافتن مسیر ریشه پروژه و افزودن به sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


# ۲. بارگذاری فایل .env.local یا .env
def load_env(base_dir: Path) -> None:
    # اولویت اول با .env.local هست، اگه نبود .env رو میخونه
    env_file = base_dir / ".env.local"
    if not env_file.exists():
        env_file = base_dir / ".env"
    
    if not env_file.exists():
        print("[WARN] هیچ فایل .env یا .env.local پیدا نشد!")
        return

    print(f"[INFO] Loading environment from: {env_file.name}")
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        # استفاده از مقداردهی مستقیم برای بازنویسی متغیرهای قبلی
        os.environ[key.strip()] = value.strip()


load_env(BASE_DIR)

from src.odoo_client.client import build_odoo_client
from src.mappers.contact_mapper import ContactMapper
from src.mappers.product_mapper import ProductMapper
from src.mappers.sale_order_mapper import SaleOrderMapper
from src.mappers.sale_order_line_mapper import SaleOrderLineMapper
from src.db.session import get_session
from src.repositories.contact_repository import ContactRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.sale_order_repository import SaleOrderRepository
from src.repositories.sale_order_line_repository import SaleOrderLineRepository


def main():
    client = build_odoo_client()
    session = get_session()

    contact_repo = ContactRepository(session)
    product_repo = ProductRepository(session)
    order_repo = SaleOrderRepository(session)
    line_repo = SaleOrderLineRepository(session)

    stats = {"created": 0, "updated": 0}

    try:
        # ---------- Contacts ----------
        print("--- Sync Contacts ---")
        contacts = ContactMapper().to_domain_list(client.fetch_contacts())
        for c in contacts:
            _, created = contact_repo.upsert(c)
            stats["created" if created else "updated"] += 1
            print(f"  {'created' if created else 'updated'}: {c.name}")

        # ---------- Products ----------
        print("\n--- Sync Products ---")
        products = ProductMapper().to_domain_list(client.fetch_products())
        for p in products:
            _, created = product_repo.upsert(p)
            stats["created" if created else "updated"] += 1
            print(f"  {'created' if created else 'updated'}: {p.name}")

        # ---------- Sale Orders ----------
        print("\n--- Sync Sale Orders ---")
        orders = SaleOrderMapper().to_domain_list(client.fetch_sale_orders())
        for o in orders:
            customer = contact_repo.get_by_odoo_id(o.customer_odoo_id)
            if customer is None:
                print(f"  [SKIP] مشتری با odoo_id={o.customer_odoo_id} پیدا نشد.")
                continue
            _, created = order_repo.upsert(o, customer_id=customer.id)
            stats["created" if created else "updated"] += 1
            print(f"  {'created' if created else 'updated'}: {o.order_number}")

        # ---------- Sale Order Lines ----------
        print("\n--- Sync Sale Order Lines ---")
        lines = SaleOrderLineMapper().to_domain_list(client.fetch_sale_order_lines())
        for line in lines:
            order = order_repo.get_by_odoo_id(line.order_odoo_id)
            product = product_repo.get_by_odoo_id(line.product_odoo_id)
            if order is None or product is None:
                print(f"  [SKIP] order یا product برای line odoo_id={line.odoo_id} پیدا نشد.")
                continue
            _, created = line_repo.upsert(line, sale_order_id=order.id, product_id=product.id)
            stats["created" if created else "updated"] += 1

        session.commit()
        print(f"\n[DONE] created={stats['created']}  updated={stats['updated']}")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
