from sqlalchemy.orm import Session

from core.entities import SaleOrderEntity
from core.interfaces import SaleOrderRepositoryInterface
from models.contacts import Contact
from models.sale_orders import SaleOrder


class SaleOrderRepository(SaleOrderRepositoryInterface):
    def __init__(self, session: Session):
        self._session = session

    def get_by_odoo_id(self, odoo_id: int) -> SaleOrder | None:
        return self._session.query(SaleOrder).filter_by(odoo_id=odoo_id).first()

    def _resolve_contact_id(self, contact_odoo_id: int) -> int:
        contact = self._session.query(Contact).filter_by(odoo_id=contact_odoo_id).first()
        if not contact:
            raise ValueError(
                f"Contact with odoo_id={contact_odoo_id} not found. "
                f"Sync contacts before syncing sale orders."
            )
        return contact.id

    def upsert(self, entity: SaleOrderEntity) -> tuple[int, bool]:
        contact_id = self._resolve_contact_id(entity.contact_odoo_id)
        existing = self.get_by_odoo_id(entity.odoo_id)

        if existing:
            existing.name = entity.name
            existing.contact_id = contact_id
            existing.date_order = entity.date_order
            existing.state = entity.state
            existing.amount_total = entity.amount_total
            self._session.flush()
            return existing.id, False

        new_order = SaleOrder(
            odoo_id=entity.odoo_id,
            name=entity.name,
            contact_id=contact_id,
            date_order=entity.date_order,
            state=entity.state,
            amount_total=entity.amount_total,
        )
        self._session.add(new_order)
        self._session.flush()
        return new_order.id, True