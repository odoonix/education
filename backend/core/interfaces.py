
from abc import ABC, abstractmethod


class ERPAdapterInterface(ABC):


    @abstractmethod
    def get_contacts(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        ...

    @abstractmethod
    def count_contacts(self) -> int:
        ...

    @abstractmethod
    def get_products(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        ...

    @abstractmethod
    def count_products(self) -> int:
        ...

    @abstractmethod
    def get_sale_orders(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        ...

    @abstractmethod
    def count_sale_orders(self) -> int:
        ...

    @abstractmethod
    def get_sale_order_lines(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        ...

    @abstractmethod
    def count_sale_order_lines(self) -> int:
        ...


from core.entities import ContactEntity


class ContactRepositoryInterface(ABC):
    @abstractmethod
    def upsert(self, entity: ContactEntity) -> tuple[int, bool]:
        ...

    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int):
        ...


from core.entities import ProductEntity, SaleOrderEntity, SaleOrderLineEntity


class ProductRepositoryInterface(ABC):
    @abstractmethod
    def upsert(self, entity: ProductEntity) -> tuple[int, bool]:
        ...

    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int):
        ...



class SaleOrderRepositoryInterface(ABC):
    @abstractmethod
    def upsert(self, entity: SaleOrderEntity) -> tuple[int, bool]:
        ...

    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int):
        ...


class SaleOrderLineRepositoryInterface(ABC):
    @abstractmethod
    def upsert(self, entity: SaleOrderLineEntity) -> tuple[int, bool]:
        ...