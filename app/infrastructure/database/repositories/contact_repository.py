from typing import Callable

from sqlalchemy.orm import Session

from app.domain.entities.contact import Contact
from app.domain.repositories.contact_repository import ContactRepository
from app.infrastructure.database.models.contact import ContactModel


class SQLAlchemyContactRepository(ContactRepository):

    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    def save(self, contact: Contact) -> None:
        session = self._session_factory()
        try:
            session.add(self._to_model(contact))
            session.commit()
        finally:
            session.close()

    def get_by_odoo_id(self, odoo_id: int) -> Contact | None:
        session = self._session_factory()
        try:
            model = session.get(ContactModel, odoo_id)
            return self._to_entity(model) if model else None
        finally:
            session.close()

    def update(self, contact: Contact) -> None:
        session = self._session_factory()
        try:
            model = session.get(ContactModel, contact.odoo_id)
            if model is None:
                return
            model.name = contact.name
            model.email = contact.email
            model.phone = contact.phone
            model.mobile = contact.mobile
            session.commit()
        finally:
            session.close()

    @staticmethod
    def _to_model(contact: Contact) -> ContactModel:
        return ContactModel(
            odoo_id=contact.odoo_id,
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            mobile=contact.mobile,
        )

    @staticmethod
    def _to_entity(model: ContactModel) -> Contact:
        return Contact(
            odoo_id=model.odoo_id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            mobile=model.mobile,
        )
