from datetime import datetime
import functools
from sqlalchemy.orm import Session

from app.integrations.odoo_client import OdooClient, OdooClientError
from app.repositories.contact_repository import ContactRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_order_repository import SaleOrderLineRepository, SaleOrderRepository
from app.repositories.sync_run_repository import SyncRunRepository, get_sync_run_repo
from app.repositories.sync_log_repository import SyncLogRepository
from app.schemas.sync import SyncEntityResult, SyncLogCreate, SyncResult, SyncRunCreate


def sync_run_decorator(sync_run_repo: SyncRunRepository = get_sync_run_repo):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = datetime.now()
            sync_run = SyncRunCreate(
                    sync_type=func.__qualname__,
                    sync_start_time=start,
                    sync_end_time=start,
                )
            # insert to db for getting sync run id
            db_sync_run=sync_run_repo.create(sync_run)
            
            try:
                result = func(*args, **kwargs, run_id=db_sync_run.id)
                if isinstance(result, SyncEntityResult):
                    sync_run.fetched_records += result.total
                    sync_run.stored_records += result.created
                    sync_run.updated_records += result.updated
                    sync_run.error_records += result.errored
                elif isinstance(result, SyncResult):
                    sync_run.fetched_records = result.contacts.total + result.products.total + result.sale_orders.total + result.sale_order_lines.total
                    sync_run.stored_records = result.contacts.created + result.products.created + result.sale_orders.created + result.sale_order_lines.created
                    sync_run.updated_records = result.contacts.updated + result.products.updated + result.sale_orders.updated + result.sale_order_lines.updated
                    sync_run.error_records = result.contacts.errored + result.products.errored + result.sale_orders.errored + result.sale_order_lines.errored
                return result

            except Exception as e:
                sync_run.sync_error = str(e)
                raise

            finally:
                sync_run.sync_end_time = datetime.now()
                # update to sync_run repository
                sync_run_repo.update(db_sync_run.id, sync_run)
        return wrapper

    return decorator

class SyncService:
    def __init__(self, db: Session, odoo: OdooClient | None = None) -> None:
        self.db = db
        self.odoo = odoo or OdooClient()
        self.contact_repo = ContactRepository(db)
        self.product_repo = ProductRepository(db)
        self.order_repo = SaleOrderRepository(db)
        self.line_repo = SaleOrderLineRepository(db)
        self.sync_log_repo = SyncLogRepository(db)

    @sync_run_decorator()
    def sync_all(self, run_id: int) -> SyncResult:
        try:
            contact_result = self._sync_contacts(run_id)
            product_result = self._sync_products(run_id)
            order_result, line_result = self._sync_sale_orders_and_lines(run_id)
            self.db.commit()
            return SyncResult(
                contacts=contact_result,
                products=product_result,
                sale_orders=order_result,
                sale_order_lines=line_result,
            )

        except Exception as exc:
            print(exc)
            self.db.rollback()
            raise exc

    def _sync_contacts(self, run_id: int) -> SyncEntityResult:
        created = updated = errored = 0
        for data in self.odoo.fetch_contacts():
            try:
                _, is_created = self.contact_repo.upsert(data)
                if is_created:
                    self.sync_log_repo.create(
                        SyncLogCreate(
                            sync_run_id=run_id,
                            level="success",
                            message="contact added to app db",
                            data=data.model_dump()
                        )
                    )
                    created += 1
                else:
                    self.sync_log_repo.create(
                        SyncLogCreate(
                            sync_run_id=run_id,
                            level="success",
                            message="contact updated in app db",
                            data=data.model_dump()
                        )
                    )
                    updated += 1
            except Exception as exc:
                self.sync_log_repo.create(
                    SyncLogCreate(
                        sync_run_id=run_id,
                        level="error",
                        message="failed to upsert contact in app db: " + str(exc),
                        data=data.model_dump()
                    )
                )
                errored +=1
        total = created + updated + errored
        return SyncEntityResult(created=created, updated=updated, errored=errored, total=total)

    def _sync_products(self, run_id: int) -> SyncEntityResult:
        created = updated = errored = 0
        for data in self.odoo.fetch_products():
            try:
                _, is_created = self.product_repo.upsert(data)
                if is_created:
                    self.sync_log_repo.create(
                        SyncLogCreate(
                            sync_run_id=run_id,
                            level="success",
                            message="product added to app db",
                            data=data.model_dump()
                        )
                    )
                    created += 1
                else:
                    self.sync_log_repo.create(
                        SyncLogCreate(
                            sync_run_id=run_id,
                            level="success",
                            message="product updated in app db",
                            data=data.model_dump()
                        )
                    )
                    updated += 1
            except Exception as exc:
                self.sync_log_repo.create(
                    SyncLogCreate(
                        sync_run_id=run_id,
                        level="error",
                        message="failed to upsert product in app db: " + str(exc),
                        data=data.model_dump()
                    )
                )
                errored +=1
        total = created + updated + errored
        return SyncEntityResult(created=created, updated=updated, errored=errored, total=total)

    def _sync_sale_orders_and_lines(self, run_id: int) -> tuple[SyncEntityResult, SyncEntityResult]:
        order_created = order_updated = order_errored = 0
        line_created = line_updated = line_errored = 0

        for order_data in self.odoo.fetch_sale_orders():
            try:
                contact = self.contact_repo.get_by_odoo_id(order_data.partner_odoo_id)
                if not contact:
                    fetched = self.odoo.fetch_contact_by_id(order_data.partner_odoo_id)
                    if fetched:
                        contact, _ = self.contact_repo.upsert(fetched)
                    else:
                        raise Exception("contact not found in local or odoo server")

                _, is_order_created = self.order_repo.upsert(order_data, contact_id=contact.id)
                if is_order_created:
                    self.sync_log_repo.create(
                        SyncLogCreate(
                            sync_run_id=run_id,
                            level="success",
                            message="order added to app db",
                            data=order_data.model_dump()
                        )
                    )
                    order_created += 1
                else:
                    self.sync_log_repo.create(
                        SyncLogCreate(
                            sync_run_id=run_id,
                            level="success",
                            message="order updated in app db",
                            data=order_data.model_dump()
                        )
                    )
                    order_updated += 1
            except Exception as exc:
                self.sync_log_repo.create(
                    SyncLogCreate(
                        sync_run_id=run_id,
                        level="error",
                        message="failed to upsert order in app db: " + str(exc),
                        data=order_data.model_dump()
                    )
                )
                errored +=1
                continue

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

                try:
                    _, is_line_created = self.line_repo.upsert(
                        line_data,
                        sale_order_id=local_order.id,
                        product_id=product_id,
                    )
                    if is_line_created:
                        self.sync_log_repo.create(
                            SyncLogCreate(
                                sync_run_id=run_id,
                                level="success",
                                message="order line added to app db",
                                data=line_data.model_dump()
                            )
                        )
                        line_created += 1
                    else:
                        self.sync_log_repo.create(
                            SyncLogCreate(
                                sync_run_id=run_id,
                                level="success",
                                message="order line updated in app db",
                                data=line_data.model_dump()
                            )
                        )
                        line_updated += 1
                except Exception as exc:
                    self.sync_log_repo.create(
                        SyncLogCreate(
                            sync_run_id=run_id,
                            level="error",
                            message="failed to upsert order line in app db: " + str(exc),
                            data=line_data.model_dump()
                        )
                    )
                    line_errored += 1

        order_total = order_created + order_updated + order_errored
        line_total = line_created + line_updated + line_errored
        return (
            SyncEntityResult(created=order_created, updated=order_updated, errored=order_errored, total=order_total),
            SyncEntityResult(created=line_created, updated=line_updated, errored=line_errored, total=line_total),
        )

    @sync_run_decorator()
    def sync_contacts(self, run_id: int) -> SyncEntityResult:
        try:
            result = self._sync_contacts(run_id)
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    @sync_run_decorator()
    def sync_products(self, run_id: int) -> SyncEntityResult:
        try:
            result = self._sync_products(run_id)
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    @sync_run_decorator()
    def sync_sale_orders(self, run_id: int) -> SyncResult:
        try:
            contact_result = self._sync_contacts(run_id)
            product_result = self._sync_products(run_id)
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
