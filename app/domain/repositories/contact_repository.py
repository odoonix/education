from abc import ABC, abstractmethod

from app.domain.entities.contact import Contact


class ContactRepository(ABC):
    
    @abstractmethod
    def save(self, contact: Contact) -> None:
        pass

    @abstractmethod
    def get_by_odoo_id(self, odoo_id: int) -> Contact | None:
        pass

    @abstractmethod
    def update(self, contact: Contact) -> None:
        pass
