from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int) -> Optional[T]:
        ...

    @abstractmethod
    def upsert(self, odoo_id: int, data: dict) -> tuple[T, bool]:
        """Create if not exists, update if exists"""
        ...
