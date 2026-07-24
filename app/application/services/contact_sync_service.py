from app.infrastructure.odoo.client import OdooClient
from app.application.dto.contact_dto import ContactDTO
from app.application.mappers.contact_mapper import ContactMapper


class ContactSyncService:

    def __init__(self, odoo_client: OdooClient):
        self.odoo_client = odoo_client
  
    def sync(self):

        contacts = self.odoo_client.get_contacts()

        entities = []

        for contact in contacts:
            dto = ContactDTO(
                odoo_id=contact["id"],
                name=contact["name"],
                email=contact.get("email") or None,
                phone=contact.get("phone") or None,
                mobile=contact.get("mobile") or None,
            )

            entity = ContactMapper.to_entity(dto)

            entities.append(entity)
        
        return entities
