"""
اسکریپت تست مرحله ۴: فقط چک می‌کنه OdooClient درست وصل میشه و می‌تونه
داده بخونه. هیچی نمی‌نویسه، فقط می‌خونه و چاپ می‌کنه.

اجرا:
    python scripts/test_odoo_connection.py
"""
import os
import sys
from pathlib import Path

# ۱. اضافه کردن مسیر پروژه به sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# ۲. تابع بارگذاری .env.local یا .env (بدون setdefault تا حتماً مقادیر اعمال شوند)
def load_env(base_dir: Path) -> None:
    # اولویت اول با .env.local است؛ اگر نبود سراغ .env می‌رود
    env_file = base_dir / ".env.local"
    if not env_file.exists():
        env_file = base_dir / ".env"

    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()


# بارگذاری فایل محیطی قبل از فراخوانی odoo_client
load_env(BASE_DIR)

# sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.odoo_client.client import build_odoo_client


def main():
    print("در حال اتصال به Odoo...")
    client = build_odoo_client()
    print("[OK] وصل شدیم.\n")

    contacts = client.fetch_contacts()
    print(f"تعداد Contacts خونده‌شده: {len(contacts)}")
    for c in contacts[:3]:
        print(f"  - {c['name']} | {c.get('email')}")

    products = client.fetch_products()
    print(f"\nتعداد Products خونده‌شده: {len(products)}")
    for p in products[:3]:
        print(
            f"  - {p['name']} | ref={p.get('default_code')} |"
            f" price={p.get('list_price')}"
        )

    orders = client.fetch_sale_orders()
    print(f"\nتعداد Sale Orders خونده‌شده: {len(orders)}")
    for o in orders[:3]:
        print(
            f"  - {o['name']} | state={o.get('state')} |"
            f" total={o.get('amount_total')}"
        )

    lines = client.fetch_sale_order_lines()
    print(f"\nتعداد Sale Order Lines خونده‌شده: {len(lines)}")


if __name__ == "__main__":
    main()
