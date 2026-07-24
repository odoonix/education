from app.db.models import Product
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository[Product]):
    model_class = Product
