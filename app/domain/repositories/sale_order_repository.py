from abc import ABC, abstractmethod

from app.domain.entities.sale_order import SaleOrder


class SaleOrderRepository(ABC):
    
    @abstractmethod
    def save(self, order: SaleOrder) -> None:
        pass

    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int) -> SaleOrder | None:
        pass

    @abstractmethod
    def update(self, order: SaleOrder) -> None:
        pass
