from app.db.models import SaleOrderLine
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class SaleOrderLineRepository(SQLAlchemyRepository[SaleOrderLine]):
    model_class = SaleOrderLine
