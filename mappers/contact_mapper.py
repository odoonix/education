from typing import Dict, Any
from models.orm_models import Contact

class ContactMapper:
    @staticmethod
    def to_internal(odoo_data: Dict[str, Any]) -> Contact:
        return Contact(
            external_id=odoo_data.get("id"),
            name=odoo_data.get("name"),
            email=odoo_data.get("email") if odoo_data.get("email") != False else None,
            phone=odoo_data.get("phone") if odoo_data.get("phone") != False else None,
            city=odoo_data.get("city") if odoo_data.get("city") != False else None,
            active=odoo_data.get("active", True)
        )