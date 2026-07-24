from abc import ABC, abstractmethod


class ErpAdapter(ABC):
    @abstractmethod
    def fetch_contacts(self, offset: int = 0, limit: int = 100, since: str | None = None) -> list[dict]:
        ...

    @abstractmethod
    def fetch_products(self, offset: int = 0, limit: int = 100, since: str | None = None) -> list[dict]:
        ...

    @abstractmethod
    def fetch_sale_orders(self, offset: int = 0, limit: int = 100, since: str | None = None) -> list[dict]:
        ...

    @abstractmethod
    def fetch_sale_order_lines(self, order_ids: list[int]) -> list[dict]:
        ...