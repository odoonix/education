from sqlalchemy.orm import Session, joinedload

from app.models.sale_order import SaleOrder, SaleOrderLine
from app.schemas.odoo_sync import OdooSaleOrderData, OdooSaleOrderLineData


class SaleOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_odoo_id(self, odoo_id: int) -> SaleOrder | None:
        return self.db.query(SaleOrder).filter(SaleOrder.odoo_id == odoo_id).first()

    def list(self, skip: int = 0, limit: int = 100) -> list[SaleOrder]:
        return (
            self.db.query(SaleOrder)
            .options(joinedload(SaleOrder.lines))
            .order_by(SaleOrder.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, order_id: int) -> SaleOrder | None:
        return (
            self.db.query(SaleOrder)
            .options(joinedload(SaleOrder.lines))
            .filter(SaleOrder.id == order_id)
            .first()
        )

    def upsert(self, data: OdooSaleOrderData, contact_id: int) -> tuple[SaleOrder, bool]:
        order = self.get_by_odoo_id(data.odoo_id)
        created = order is None
        if created:
            order = SaleOrder(odoo_id=data.odoo_id)

        order.name = data.name
        order.contact_id = contact_id
        order.state = data.state
        order.amount_total = data.amount_total
        order.date_order = data.date_order

        self.db.add(order)
        self.db.flush()
        return order, created


class SaleOrderLineRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_odoo_id(self, odoo_id: int) -> SaleOrderLine | None:
        return self.db.query(SaleOrderLine).filter(SaleOrderLine.odoo_id == odoo_id).first()

    def upsert(
        self,
        data: OdooSaleOrderLineData,
        sale_order_id: int,
        product_id: int | None,
    ) -> tuple[SaleOrderLine, bool]:
        line = self.get_by_odoo_id(data.odoo_id)
        created = line is None
        if created:
            line = SaleOrderLine(odoo_id=data.odoo_id)

        line.sale_order_id = sale_order_id
        line.product_id = product_id
        line.name = data.name
        line.product_uom_qty = data.product_uom_qty
        line.price_unit = data.price_unit
        line.price_subtotal = data.price_subtotal

        self.db.add(line)
        self.db.flush()
        return line, created
