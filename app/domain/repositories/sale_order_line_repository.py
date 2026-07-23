from abc import ABC, abstractmethod

from app.domain.entities.sale_order_line import SaleOrderLine


class SaleOrderLineRepository(ABC):
    
    @abstractmethod
    def save(self, line: SaleOrderLine) -> None:
        pass

    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int) -> SaleOrderLine | None:
        pass

    @abstractmethod
    def update(self, line: SaleOrderLine) -> None:
        pass