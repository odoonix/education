from app.application.dto.contact_dto import ContactDTO
from app.domain.entities.contact import Contact


class ContactMapper:

    @staticmethod
    def to_entity(dto: ContactDTO) -> Contact:
        return Contact(
            odoo_id=dto.odoo_id,
            name=dto.name,
            email=dto.email,
            phone=dto.phone,
            mobile=dto.mobile,
        )
