from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import OdooContact


class ContactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_odoo_id(
        self,
        odoo_id: int,
    ) -> Contact | None:
        statement = select(Contact).where(
            Contact.odoo_id == odoo_id,
        )

        return self._session.scalar(statement)

    def create(
        self,
        contact_data: OdooContact,
    ) -> Contact:
        contact = Contact(
            odoo_id=contact_data.odoo_id,
            name=contact_data.name,
            email=contact_data.email,
            phone=contact_data.phone,
            mobile=contact_data.mobile,
        )

        self._session.add(contact)

        return contact

    def update(
        self,
        contact: Contact,
        contact_data: OdooContact,
    ) -> Contact:
        contact.name = contact_data.name
        contact.email = contact_data.email
        contact.phone = contact_data.phone
        contact.mobile = contact_data.mobile

        return contact