
from sqlalchemy.orm import Session

from core.entities import ContactEntity
from core.interfaces import ContactRepositoryInterface
from models.contacts import Contact


class ContactRepository(ContactRepositoryInterface):
    def __init__(self, session: Session):
        self._session = session

    def get_by_odoo_id(self, odoo_id: int) -> Contact | None:
        return self._session.query(Contact).filter_by(odoo_id=odoo_id).first()

    def upsert(self, entity: ContactEntity) -> tuple[int, bool]:
        existing = self.get_by_odoo_id(entity.odoo_id)

        if existing:
            existing.name = entity.name
            existing.email = entity.email
            existing.phone = entity.phone
            existing.mobile = entity.mobile
            self._session.flush()
            return existing.id, False

        new_contact = Contact(
            odoo_id=entity.odoo_id,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            mobile=entity.mobile,
        )
        self._session.add(new_contact)
        self._session.flush()
        return new_contact.id, True