from sqlalchemy.orm import Session

from app.integrations.odoo_client import OdooClient, OdooClientError
from app.repositories.contact_repository import ContactRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_order_repository import SaleOrderLineRepository, SaleOrderRepository
from app.schemas.sync import SyncEntityResult, SyncResult


class SyncService:
    def __init__(self, db: Session, odoo: OdooClient | None = None) -> None:
        self.db = db
        self.odoo = odoo or OdooClient()
        self.contact_repo = ContactRepository(db)
        self.product_repo = ProductRepository(db)
        self.order_repo = SaleOrderRepository(db)
        self.line_repo = SaleOrderLineRepository(db)

    def sync_all(self) -> SyncResult:
        try:
            contact_result = self._sync_contacts()
            product_result = self._sync_products()
            order_result, line_result = self._sync_sale_orders_and_lines()
            self.db.commit()
            return SyncResult(
                contacts=contact_result,
                products=product_result,
                sale_orders=order_result,
                sale_order_lines=line_result,
            )
        except Exception:
            self.db.rollback()
            raise

    def _sync_contacts(self) -> SyncEntityResult:
        created = updated = 0
        for data in self.odoo.fetch_contacts():
            _, is_created = self.contact_repo.upsert(data)
            if is_created:
                created += 1
            else:
                updated += 1
        total = created + updated
        return SyncEntityResult(created=created, updated=updated, total=total)

    def _sync_products(self) -> SyncEntityResult:
        created = updated = 0
        for data in self.odoo.fetch_products():
            _, is_created = self.product_repo.upsert(data)
            if is_created:
                created += 1
            else:
                updated += 1
        total = created + updated
        return SyncEntityResult(created=created, updated=updated, total=total)

    def _sync_sale_orders_and_lines(self) -> tuple[SyncEntityResult, SyncEntityResult]:
        order_created = order_updated = 0
        line_created = line_updated = 0

        for order_data in self.odoo.fetch_sale_orders():
            contact = self.contact_repo.get_by_odoo_id(order_data.partner_odoo_id)
            if not contact:
                fetched = self.odoo.fetch_contact_by_id(order_data.partner_odoo_id)
                if fetched:
                    contact, _ = self.contact_repo.upsert(fetched)
                else:
                    continue

            _, is_order_created = self.order_repo.upsert(order_data, contact_id=contact.id)
            if is_order_created:
                order_created += 1
            else:
                order_updated += 1

            local_order = self.order_repo.get_by_odoo_id(order_data.odoo_id)
            if not local_order:
                continue

            lines = self.odoo.fetch_sale_order_lines(order_data.line_odoo_ids)
            for line_data in lines:
                product_id = None
                if line_data.product_odoo_id:
                    product = self.product_repo.get_by_odoo_id(line_data.product_odoo_id)
                    if not product:
                        fetched_product = self.odoo.fetch_product_by_id(line_data.product_odoo_id)
                        if fetched_product:
                            product, _ = self.product_repo.upsert(fetched_product)
                    if product:
                        product_id = product.id

                _, is_line_created = self.line_repo.upsert(
                    line_data,
                    sale_order_id=local_order.id,
                    product_id=product_id,
                )
                if is_line_created:
                    line_created += 1
                else:
                    line_updated += 1

        order_total = order_created + order_updated
        line_total = line_created + line_updated
        return (
            SyncEntityResult(created=order_created, updated=order_updated, total=order_total),
            SyncEntityResult(created=line_created, updated=line_updated, total=line_total),
        )

    def sync_contacts(self) -> SyncEntityResult:
        try:
            result = self._sync_contacts()
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    def sync_products(self) -> SyncEntityResult:
        try:
            result = self._sync_products()
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    def sync_sale_orders(self) -> SyncResult:
        try:
            contact_result = self._sync_contacts()
            product_result = self._sync_products()
            order_result, line_result = self._sync_sale_orders_and_lines()
            self.db.commit()
            return SyncResult(
                contacts=contact_result,
                products=product_result,
                sale_orders=order_result,
                sale_order_lines=line_result,
            )
        except Exception:
            self.db.rollback()
            raise
