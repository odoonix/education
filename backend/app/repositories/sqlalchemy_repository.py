from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.repositories.base_repository import AbstractRepository

T = TypeVar("T")


class SQLAlchemyRepository(AbstractRepository[T], Generic[T]):
    model_class: Type[T]

    def __init__(self, session: Session):
        self.session = session

    def get_by_odoo_id(self, odoo_id: int) -> Optional[T]:
        return (
            self.session.query(self.model_class)
            .filter_by(odoo_id=odoo_id)
            .first()
        )

    def get_by_id(self, internal_id: int) -> Optional[T]:
        return self.session.get(self.model_class, internal_id)

    def upsert(self, odoo_id: int, data: dict) -> tuple[T, bool]:
        existing = self.get_by_odoo_id(odoo_id)
        if existing is not None:
            for key, value in data.items():
                setattr(existing, key, value)
            self.session.flush()
            return existing, False

        entity = self.model_class(odoo_id=odoo_id, **data)
        self.session.add(entity)
        self.session.flush()
        return entity, True
