from app.domain.entities.sale_order_line import SaleOrderLine
from app.domain.ports.db_session import IDBConnection
from app.domain.repositories.sale_order_line_repository import SaleOrderLineRepository
from app.infrastructure.database.models.sale_order_line import SaleOrderLineModel


class SQLAlchemySaleOrderLineRepository(SaleOrderLineRepository):

    def __init__(self, db_connection: IDBConnection):
        self._db = db_connection

    def save(self, line: SaleOrderLine) -> None:
        session = self._db.get_session()
        try:
            session.add(self._to_model(line))
            session.commit()
        finally:
            session.close()

    def get_by_odoo_id(self, odoo_id: int) -> SaleOrderLine | None:
        session = self._db.get_session()
        try:
            model = session.get(SaleOrderLineModel, odoo_id)
            return self._to_entity(model) if model else None
        finally:
            session.close()

    def update(self, line: SaleOrderLine) -> None:
        session = self._db.get_session()
        try:
            model = session.get(SaleOrderLineModel, line.odoo_id)
            if model is None:
                return
            model.sale_order_id = line.sale_order_id
            model.product_id = line.product_id
            model.quantity = line.quantity
            model.unit_price = line.unit_price
            model.subtotal = line.subtotal
            session.commit()
        finally:
            session.close()

    @staticmethod
    def _to_model(line: SaleOrderLine) -> SaleOrderLineModel:
        return SaleOrderLineModel(
            odoo_id=line.odoo_id,
            sale_order_id=line.sale_order_id,
            product_id=line.product_id,
            quantity=line.quantity,
            unit_price=line.unit_price,
            subtotal=line.subtotal,
        )

    @staticmethod
    def _to_entity(model: SaleOrderLineModel) -> SaleOrderLine:
        return SaleOrderLine(
            odoo_id=model.odoo_id,
            sale_order_id=model.sale_order_id,
            product_id=model.product_id,
            quantity=model.quantity,
            unit_price=model.unit_price,
            subtotal=model.subtotal,
        )
