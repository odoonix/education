from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar(
    "ModelType",
    bound=Base,
)


class BaseRepository(Generic[ModelType]):

    def __init__(
        self,
        session: Session,
        model: type[ModelType],
    ):
        self.session = session
        self.model = model

    def get_by_id(
        self,
        record_id: int,
    ):
        result = self.session.execute(
            select(self.model)
            .where(
                self.model.id == record_id
            )
        )

        return result.scalar_one_or_none()

    def get_all(self):
        result = self.session.execute(
            select(self.model)
        )

        return result.scalars().all()

    def create(
        self,
        obj: ModelType,
    ):
        self.session.add(obj)
        self.session.flush()

        return obj

    def delete(
        self,
        obj: ModelType,
    ):
        self.session.delete(obj)
