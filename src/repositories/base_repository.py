"""
BaseRepository منطق مشترک همه‌ی Repositoryها رو یک‌جا پیاده می‌کنه:
- get_by_odoo_id: پیدا کردن رکورد موجود
- upsert: اگه بود Update کن، نبود Insert کن (این دقیقاً همون Idempotent Design هست)

هر Repository فرزند (ContactRepository, ProductRepository, ...) فقط باید
بگه «فیلدهای Domain Model چطور به ستون‌های ORM نگاشت میشن» — این کار تو
متد _to_orm_kwargs انجام میشه.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
DomainType = TypeVar("DomainType")


class BaseRepository(ABC, Generic[ModelType, DomainType]):
    model_class: type[ModelType]

    def __init__(self, session: Session):
        self.session = session

    def get_by_odoo_id(self, odoo_id: int) -> Optional[ModelType]:
        return (
            self.session.query(self.model_class)
            .filter_by(odoo_id=odoo_id)
            .first()
        )

    @abstractmethod
    def _to_orm_kwargs(self, domain: DomainType, **extra: Any) -> dict[str, Any]:
        """فیلدهای Domain Model رو به دیکشنری مناسب برای ساخت/آپدیت ORM تبدیل می‌کنه."""
        raise NotImplementedError

    def upsert(self, domain: DomainType, **extra: Any) -> tuple[ModelType, bool]:
        """
        خروجی: (شیء ORM ذخیره‌شده، آیا تازه ساخته شد یا آپدیت شد)

        نکته: اینجا commit نمی‌کنیم! فقط flush می‌کنیم تا id بگیره ولی
        Transaction هنوز باز بمونه. تصمیم commit/rollback با Service Layer هست
        (چون اونجاست که "کل عملیات موفق بود یا نه" مشخص میشه).
        """
        existing = self.get_by_odoo_id(domain.odoo_id)
        kwargs = self._to_orm_kwargs(domain, **extra)

        if existing:
            for key, value in kwargs.items():
                setattr(existing, key, value)
            self.session.flush()
            return existing, False

        new_obj = self.model_class(**kwargs)
        self.session.add(new_obj)
        self.session.flush()
        return new_obj, True
