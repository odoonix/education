from app.db.models import SaleOrder
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class SaleOrderRepository(SQLAlchemyRepository[SaleOrder]):
    model_class = SaleOrder
