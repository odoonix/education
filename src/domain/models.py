"""
Domain Models: این کلاس‌ها هیچ ارتباطی با Odoo یا SQLAlchemy ندارن. فقط
داده‌ی «تمیز و معنادار» رو نگه می‌دارن. اگه فردا Odoo عوض شد به یه سیستم
دیگه، یا دیتابیس عوض شد، این کلاس‌ها دست‌نخورده می‌مونن.

از dataclass استفاده کردیم چون برای نگه‌داشتن ساده‌ی داده، از تعریف دستی
__init__ و __repr__ راحت‌تره.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Contact:
    odoo_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None


@dataclass
class Product:
    odoo_id: int
    name: str
    internal_reference: Optional[str] = None
    sale_price: float = 0.0
    product_type: Optional[str] = None


@dataclass
class SaleOrder:
    odoo_id: int
    order_number: str
    customer_odoo_id: int  # فقط شناسه‌ی Odoo مشتری؛ تبدیل به FK داخلی کار Repository هست
    order_date: Optional[datetime] = None
    state: Optional[str] = None
    total_amount: float = 0.0


@dataclass
class SaleOrderLine:
    odoo_id: int
    order_odoo_id: int
    product_odoo_id: int
    quantity: float = 0.0
    unit_price: float = 0.0
    subtotal: float = 0.0
