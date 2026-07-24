from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sale_order_line import SaleOrderLine
from app.schemas.sale_order import OdooSaleOrderLine


class SaleOrderLineRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_odoo_id(
        self,
        odoo_id: int,
    ) -> SaleOrderLine | None:
        statement = select(SaleOrderLine).where(
            SaleOrderLine.odoo_id == odoo_id,
        )

        return self._session.scalar(statement)

    def create(
        self,
        sale_order_line_data: OdooSaleOrderLine,
        product_id: int,
        sale_order_id: int,
    ) -> SaleOrderLine:
        sale_order_line = SaleOrderLine(
            odoo_id=sale_order_line_data.odoo_id,
            product_id=product_id,
            sale_order_id=sale_order_id,
            quantity=sale_order_line_data.quantity,
            unit_price=sale_order_line_data.unit_price,
            subtotal=sale_order_line_data.subtotal,
        )

        self._session.add(sale_order_line)

        return sale_order_line

    def update(
        self,
        sale_order_line: SaleOrderLine,
        sale_order_line_data: OdooSaleOrderLine,
        product_id: int,
        sale_order_id: int,
    ) -> SaleOrderLine:
        sale_order_line.product_id = product_id
        sale_order_line.sale_order_id = sale_order_id
        sale_order_line.quantity = sale_order_line_data.quantity
        sale_order_line.unit_price = sale_order_line_data.unit_price
        sale_order_line.subtotal = sale_order_line_data.subtotal

        return sale_order_line