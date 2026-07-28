"""
اسکریپت تست مرحله ۵: چک می‌کنه Mapperها درست کار می‌کنن.

اجرا:
    python scripts/test_mapping.py
"""

import os
import sys
from pathlib import Path

# ۱. افزودن مسیر اصلی پروژه به sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


# ۲. بارگذاری فایل .env.local یا .env
def load_env(base_dir: Path) -> None:
    # اولویت اول با .env.local، در غیر این صورت .env
    env_file = base_dir / ".env.local"
    if not env_file.exists():
        env_file = base_dir / ".env"

    if not env_file.exists():
        return

    print(f"[INFO] Loading environment from: {env_file.name}")
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()


load_env(BASE_DIR)

from src.odoo_client.client import build_odoo_client
from src.mappers.contact_mapper import ContactMapper
from src.mappers.product_mapper import ProductMapper
from src.mappers.sale_order_mapper import SaleOrderMapper
from src.mappers.sale_order_line_mapper import SaleOrderLineMapper


def main():
    client = build_odoo_client()

    print("--- Contacts ---")
    raw_contacts = client.fetch_contacts()
    contacts = ContactMapper().to_domain_list(raw_contacts)
    for c in contacts:
        print(" ", c)

    print("\n--- Products ---")
    raw_products = client.fetch_products()
    products = ProductMapper().to_domain_list(raw_products)
    for p in products:
        print(" ", p)

    print("\n--- Sale Orders ---")
    raw_orders = client.fetch_sale_orders()
    orders = SaleOrderMapper().to_domain_list(raw_orders)
    for o in orders:
        print(" ", o)

    print("\n--- Sale Order Lines ---")
    raw_lines = client.fetch_sale_order_lines()
    lines = SaleOrderLineMapper().to_domain_list(raw_lines)
    for l in lines:
        print(" ", l)


if __name__ == "__main__":
    main()
