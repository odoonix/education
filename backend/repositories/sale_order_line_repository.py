from sqlalchemy.orm import Session

from core.entities import SaleOrderLineEntity
from core.interfaces import SaleOrderLineRepositoryInterface
from models.product import Product
from models.sale_orders import SaleOrder
from models.sale_order_lines import SaleOrderLine


class SaleOrderLineRepository(SaleOrderLineRepositoryInterface):
    def __init__(self, session: Session):
        self._session = session

    def get_by_odoo_id(self, odoo_id: int) -> SaleOrderLine | None:
        return self._session.query(SaleOrderLine).filter_by(odoo_id=odoo_id).first()

    def _resolve_sale_order_id(self, order_odoo_id: int) -> int:
        order = self._session.query(SaleOrder).filter_by(odoo_id=order_odoo_id).first()
        if not order:
            raise ValueError(f"SaleOrder with odoo_id={order_odoo_id} not found.")
        return order.id

    def _resolve_product_id(self, product_odoo_id: int) -> int:
        product = self._session.query(Product).filter_by(odoo_id=product_odoo_id).first()
        if not product:
            raise ValueError(f"Product with odoo_id={product_odoo_id} not found.")
        return product.id

    def upsert(self, entity: SaleOrderLineEntity) -> tuple[int, bool]:
        sale_order_id = self._resolve_sale_order_id(entity.sale_order_odoo_id)
        product_id = self._resolve_product_id(entity.product_odoo_id)
        existing = self.get_by_odoo_id(entity.odoo_id)

        if existing:
            existing.sale_order_id = sale_order_id
            existing.product_id = product_id
            existing.quantity = entity.quantity
            existing.price_unit = entity.unit_price
            existing.subtotal = entity.subtotal
            self._session.flush()
            return existing.id, False

        new_line = SaleOrderLine(
            odoo_id=entity.odoo_id,
            sale_order_id=sale_order_id,
            product_id=product_id,
            quantity=entity.quantity,
            price_unit=entity.unit_price,
            subtotal=entity.subtotal,
        )
        self._session.add(new_line)
        self._session.flush()
        return new_line.id, True