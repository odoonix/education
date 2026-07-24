from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sale_order import SaleOrder
from app.schemas.sale_order import OdooSaleOrder


class SaleOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_odoo_id(
        self,
        odoo_id: int,
    ) -> SaleOrder | None:
        statement = select(SaleOrder).where(
            SaleOrder.odoo_id == odoo_id,
        )

        return self._session.scalar(statement)

    def create(
        self,
        sale_order_data: OdooSaleOrder,
        contact_id: int,
    ) -> SaleOrder:
        sale_order = SaleOrder(
            odoo_id=sale_order_data.odoo_id,
            order_number=sale_order_data.order_number,
            contact_id=contact_id,
            order_date=sale_order_data.order_date,
            state=sale_order_data.state,
            total_amount=sale_order_data.total_amount,
        )

        self._session.add(sale_order)

        return sale_order

    def update(
        self,
        sale_order: SaleOrder,
        sale_order_data: OdooSaleOrder,
        contact_id: int,
    ) -> SaleOrder:
        sale_order.order_number = sale_order_data.order_number
        sale_order.contact_id = contact_id
        sale_order.order_date = sale_order_data.order_date
        sale_order.state = sale_order_data.state
        sale_order.total_amount = sale_order_data.total_amount

        return sale_order