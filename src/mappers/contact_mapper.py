from typing import Any

from src.domain.models import Contact
from src.mappers.base_mapper import BaseMapper


class ContactMapper(BaseMapper[Contact]):
    def to_domain(self, raw: dict[str, Any]) -> Contact:
        return Contact(
            odoo_id=raw["id"],
            name=raw["name"],
            email=raw.get("email") or None,
            phone=raw.get("phone") or None,
            mobile=raw.get("mobile") or None,
        )
