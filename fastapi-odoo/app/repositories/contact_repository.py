from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.odoo_sync import OdooContactData


class ContactRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_odoo_id(self, odoo_id: int) -> Contact | None:
        return self.db.query(Contact).filter(Contact.odoo_id == odoo_id).first()

    def list(self, skip: int = 0, limit: int = 100) -> list[Contact]:
        return (
            self.db.query(Contact)
            .order_by(Contact.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def upsert(self, data: OdooContactData) -> tuple[Contact, bool]:
        contact = self.get_by_odoo_id(data.odoo_id)
        created = contact is None
        if created:
            contact = Contact(odoo_id=data.odoo_id)

        contact.name = data.name
        contact.email = data.email
        contact.phone = data.phone
        contact.street = data.street
        contact.city = data.city
        contact.country = data.country
        contact.is_company = data.is_company

        self.db.add(contact)
        self.db.flush()
        return contact, created
