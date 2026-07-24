from abc import ABC, abstractmethod

from app.domain.entities.product import Product


class ProductRepository(ABC):
    
    @abstractmethod
    def save(self, product: Product) -> None:
        pass

    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int) -> Product | None:
        pass

    @abstractmethod
    def update(self, product: Product) -> None:
        pass