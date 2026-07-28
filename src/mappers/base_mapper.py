"""
BaseMapper یک قرارداد (Interface) مشخص می‌کنه: هر Mapper باید یک متد
to_domain داشته باشه که dict خام Odoo رو می‌گیره و یک Domain Model برمی‌گردونه.

این همون "Abstract Class" ایه که تو مصاحبه ازت پرسیدن. کلاس‌های فرزند
(ContactMapper, ProductMapper, ...) این متد رو پیاده‌سازی می‌کنن.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseMapper(ABC, Generic[T]):
    @abstractmethod
    def to_domain(self, raw: dict[str, Any]) -> T:
        """dict خام Odoo رو به یک Domain Model تبدیل می‌کنه."""
        raise NotImplementedError

    def to_domain_list(self, raw_list: list[dict[str, Any]]) -> list[T]:
        """میان‌بر راحت برای تبدیل یک لیست از رکوردهای خام."""
        return [self.to_domain(raw) for raw in raw_list]


def extract_many2one_id(value: Any) -> int | None:
    """
    فیلدهای Many2One تو Odoo به‌شکل [id, "display name"] برمی‌گردن،
    یا وقتی خالی باشن False هستن. این تابع فقط id رو استخراج می‌کنه.
    """
    if not value:
        return None
    if isinstance(value, (list, tuple)):
        return value[0]
    return value
