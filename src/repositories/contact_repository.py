from typing import Any

from src.db.models import Contact as ContactORM
from src.domain.models import Contact as ContactDomain
from src.repositories.base_repository import BaseRepository


class ContactRepository(BaseRepository[ContactORM, ContactDomain]):
    model_class = ContactORM

    def _to_orm_kwargs(self, domain: ContactDomain, **extra: Any) -> dict[str, Any]:
        return {
            "odoo_id": domain.odoo_id,
            "name": domain.name,
            "email": domain.email,
            "phone": domain.phone,
            "mobile": domain.mobile,
        }
