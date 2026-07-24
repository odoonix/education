from app.db.models import Contact
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class ContactRepository(SQLAlchemyRepository[Contact]):
    model_class = Contact
