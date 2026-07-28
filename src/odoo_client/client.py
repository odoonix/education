"""
این ماژول تنها جاییه که مستقیم با XML-RPC Odoo کار می‌کنه.
بقیه‌ی پروژه (Service Layer) فقط از متدهای این کلاس (fetch_contacts,
fetch_products, ...) استفاده می‌کنه و نمی‌دونه پشت‌پرده XML-RPC هست یا
هر چیز دیگه — اگه فردا Odoo رو با یه پروتکل دیگه صدا زدیم، فقط همین فایل
عوض میشه.
"""

import xmlrpc.client
from datetime import datetime
from typing import Any

from src.config.settings import settings
from src.core.retry import retry


class OdooConnectionError(Exception):
    """وقتی اتصال یا احراز هویت با Odoo شکست بخوره."""


class OdooClient:
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self._uid: int | None = None
        self._models = None

    # ---------- اتصال ----------
    @retry(
        times=5,
        delay=2.0,
        backoff=1.5,
        exceptions=(ConnectionError, OSError, TimeoutError, xmlrpc.client.ProtocolError),
    )
    def connect(self) -> "OdooClient":
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        # نکته: authenticate رو دیگه تو try/except عمومی نمی‌گیریم که
        # اگه ارور شبکه‌ای بود (مثلاً Odoo خاموشه)، بذاریم بره بالا و
        # retry decorator بگیرتش. فقط خطای غیرمنتظره‌ی دیگه رو تبدیل
        # به OdooConnectionError می‌کنیم.
        uid = common.authenticate(self.db, self.username, self.password, {})

        if not uid:
            # پسورد/یوزرنیم/دیتابیس غلطه -- این یه خطای شبکه‌ای نیست، پس
            # retry روش فایده‌ای نداره و بلافاصله باید گزارش بشه.
            raise OdooConnectionError(
                "احراز هویت ناموفق بود؛ یوزرنیم/پسورد یا اسم دیتابیس رو چک کن."
            )

        self._uid = uid
        self._models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        return self

    def _ensure_connected(self):
        if self._uid is None or self._models is None:
            raise OdooConnectionError("قبل از استفاده باید connect() صدا زده بشه.")

    # ---------- متد عمومی برای خوندن با Pagination ----------
    @retry(
        times=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(ConnectionError, OSError, TimeoutError, xmlrpc.client.ProtocolError),
    )
    def search_read(
        self,
        model: str,
        domain: list | None = None,
        fields: list[str] | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        self._ensure_connected()
        domain = domain or []
        fields = fields or []
        return self._models.execute_kw(
            self.db, self._uid, self.password,
            model, "search_read",
            [domain],
            {"fields": fields, "offset": offset, "limit": limit},
        )

    def search_read_all(
        self,
        model: str,
        domain: list | None = None,
        fields: list[str] | None = None,
        page_size: int = 100,
    ) -> list[dict[str, Any]]:
        """
        همه‌ی رکوردها رو صفحه‌به‌صفحه (Batch) می‌خونه، نه یک‌جا. برای حجم زیاد
        داده لازمه که همه‌چیز رو با یک درخواست از Odoo نگیریم.
        """
        all_records: list[dict[str, Any]] = []
        offset = 0
        while True:
            page = self.search_read(model, domain, fields, offset=offset, limit=page_size)
            if not page:
                break
            all_records.extend(page)
            offset += page_size
        return all_records

    # ---------- متدهای اختصاصی هر مدل ----------
    # همه‌شون پارامتر اختیاری `since` دارن: اگه پاس داده بشه، فقط رکوردهایی
    # که از اون تاریخ به بعد تو Odoo تغییر کردن (write_date) برگردونده میشن
    # -- این همون Incremental Sync هست، به‌جای خوندن کل جدول هر بار.

    def fetch_contacts(self, since: "datetime | None" = None) -> list[dict[str, Any]]:
        domain: list = [["email", "!=", False]]
        if since is not None:
            domain.append(["write_date", ">=", since.strftime("%Y-%m-%d %H:%M:%S")])
        return self.search_read_all(
            "res.partner",
            domain=domain,
            fields=["id", "name", "email", "phone", "mobile"],
        )

    def fetch_products(self, since: "datetime | None" = None) -> list[dict[str, Any]]:
        domain: list = []
        if since is not None:
            domain.append(["write_date", ">=", since.strftime("%Y-%m-%d %H:%M:%S")])
        return self.search_read_all(
            "product.product",
            domain=domain,
            fields=["id", "name", "default_code", "list_price", "type"],
        )

    def fetch_sale_orders(self, since: "datetime | None" = None) -> list[dict[str, Any]]:
        domain: list = []
        if since is not None:
            domain.append(["write_date", ">=", since.strftime("%Y-%m-%d %H:%M:%S")])
        return self.search_read_all(
            "sale.order",
            domain=domain,
            fields=["id", "name", "partner_id", "date_order", "state", "amount_total"],
        )

    def fetch_sale_order_lines(self, since: "datetime | None" = None) -> list[dict[str, Any]]:
        domain: list = [["display_type", "=", False]]  # حذف خط‌های section/note که محصول ندارن
        if since is not None:
            domain.append(["write_date", ">=", since.strftime("%Y-%m-%d %H:%M:%S")])
        return self.search_read_all(
            "sale.order.line",
            domain=domain,
            fields=["id", "order_id", "product_id", "product_uom_qty", "price_unit", "price_subtotal"],
        )


def build_odoo_client() -> OdooClient:
    """
    یک OdooClient آماده و متصل برمی‌گردونه، با استفاده از تنظیمات
    داخل src/config/settings.py (که از .env می‌خونه).
    بقیه‌ی کد پروژه به‌جای ساختن دستی OdooClient، همین تابع رو صدا می‌زنه.
    """
    client = OdooClient(
        url=settings.ODOO_URL,
        db=settings.ODOO_DB,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD,
    )
    return client.connect()
