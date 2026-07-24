from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):

    def __init__(
        self,
        session: Session,
    ):
        super().__init__(
            session,
            Contact,
        )
