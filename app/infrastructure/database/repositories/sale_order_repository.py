from app.domain.entities.sale_order import SaleOrder
from app.domain.ports.db_session import IDBConnection
from app.domain.repositories.sale_order_repository import SaleOrderRepository
from app.infrastructure.database.models.sale_order import SaleOrderModel


class SQLAlchemySaleOrderRepository(SaleOrderRepository):

    def __init__(self, db_connection: IDBConnection):
        self._db = db_connection

    def save(self, order: SaleOrder) -> None:
        session = self._db.get_session()
        try:
            session.add(self._to_model(order))
            session.commit()
        finally:
            session.close()

    def get_by_odoo_id(self, odoo_id: int) -> SaleOrder | None:
        session = self._db.get_session()
        try:
            model = session.get(SaleOrderModel, odoo_id)
            return self._to_entity(model) if model else None
        finally:
            session.close()

    def update(self, order: SaleOrder) -> None:
        session = self._db.get_session()
        try:
            model = session.get(SaleOrderModel, order.odoo_id)
            if model is None:
                return
            model.order_number = order.order_number
            model.customer_id = order.customer_id
            model.order_date = order.order_date
            model.state = order.state
            model.total_amount = order.total_amount
            session.commit()
        finally:
            session.close()

    @staticmethod
    def _to_model(order: SaleOrder) -> SaleOrderModel:
        return SaleOrderModel(
            odoo_id=order.odoo_id,
            order_number=order.order_number,
            customer_id=order.customer_id,
            order_date=order.order_date,
            state=order.state,
            total_amount=order.total_amount,
        )

    @staticmethod
    def _to_entity(model: SaleOrderModel) -> SaleOrder:
        return SaleOrder(
            odoo_id=model.odoo_id,
            order_number=model.order_number,
            customer_id=model.customer_id,
            order_date=model.order_date,
            state=model.state,
            total_amount=model.total_amount,
        )
