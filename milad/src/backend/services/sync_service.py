import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.adapters.base import ErpAdapter
from backend.adapters.odoo_adapter import OdooConnectionError
from backend.domain.mappers import map_contact, map_product, map_sale_order, map_sale_order_line
from backend.infrastructure.db_models import SyncLogModel, SyncRunModel
from backend.repositories.repositories import (
    ContactRepository,
    ProductRepository,
    SaleOrderRepository,
)

logger = logging.getLogger(__name__)


class SyncResult:
    def __init__(self) -> None:
        self.fetched = 0
        self.created = 0
        self.updated = 0
        self.errors = 0


class SyncService:
    def __init__(self, session: Session, odoo: ErpAdapter, batch_size: int = 100) -> None:
        self._session = session
        self._odoo = odoo
        self._batch_size = batch_size
        self._contacts = ContactRepository(session)
        self._products = ProductRepository(session)
        self._orders = SaleOrderRepository(session)

    def run_full_sync(self) -> SyncRunModel:
        return self._run(operation="full_sync", since=None)

    def run_incremental_sync(self) -> SyncRunModel:
        since = self._last_successful_sync_timestamp()
        return self._run(operation="incremental_sync", since=since)

    def _run(self, operation: str, since: str | None) -> SyncRunModel:
        run = SyncRunModel(operation=operation, started_at=datetime.now(timezone.utc))
        self._session.add(run)
        self._session.flush()

        result = SyncResult()

        try:
            self._sync_contacts(run, result, since)
            self._sync_products(run, result, since)
            self._sync_sale_orders(run, result, since)
            self._session.commit()
        except Exception as exc:
            self._session.rollback()
            self._log(run, "error", f"Sync aborted: {exc}")
            raise
        finally:
            run.finished_at = datetime.now(timezone.utc)
            run.fetched_count = result.fetched
            run.created_count = result.created
            run.updated_count = result.updated
            run.error_count = result.errors
            self._session.add(run)
            self._session.commit()

        return run

    def _last_successful_sync_timestamp(self) -> str | None:
        last_run = (
            self._session.query(SyncRunModel)
            .filter(SyncRunModel.error_count == 0)
            .filter(SyncRunModel.finished_at.isnot(None))
            .order_by(SyncRunModel.finished_at.desc())
            .first()
        )
        if last_run is None:
            return None
        return last_run.finished_at.strftime("%Y-%m-%d %H:%M:%S")

    def _sync_contacts(self, run: SyncRunModel, result: SyncResult, since: str | None) -> None:
        offset = 0
        while True:
            batch = self._fetch_with_retry(self._odoo.fetch_contacts, offset, self._batch_size, since)
            if not batch:
                break

            for raw in batch:
                result.fetched += 1
                try:
                    contact = map_contact(raw)
                    _, created = self._contacts.upsert(contact)
                    result.created += int(created)
                    result.updated += int(not created)
                except Exception as exc:
                    result.errors += 1
                    self._log(run, "error", f"Contact sync failed: {exc}", raw.get("id"))

            offset += self._batch_size

    def _sync_products(self, run: SyncRunModel, result: SyncResult, since: str | None) -> None:
        offset = 0
        while True:
            batch = self._fetch_with_retry(self._odoo.fetch_products, offset, self._batch_size, since)
            if not batch:
                break

            for raw in batch:
                result.fetched += 1
                try:
                    product = map_product(raw)
                    _, created = self._products.upsert(product)
                    result.created += int(created)
                    result.updated += int(not created)
                except Exception as exc:
                    result.errors += 1
                    self._log(run, "error", f"Product sync failed: {exc}", raw.get("id"))

            offset += self._batch_size

    def _sync_sale_orders(self, run: SyncRunModel, result: SyncResult, since: str | None) -> None:
        offset = 0
        while True:
            batch = self._fetch_with_retry(self._odoo.fetch_sale_orders, offset, self._batch_size, since)
            if not batch:
                break

            order_ids = [raw["id"] for raw in batch]
            raw_lines_by_order = self._group_lines_by_order(order_ids)

            for raw in batch:
                result.fetched += 1
                try:
                    is_new = self._sync_single_order(raw, raw_lines_by_order.get(raw["id"], []))
                    result.created += int(is_new)
                    result.updated += int(not is_new)
                except Exception as exc:
                    result.errors += 1
                    self._log(run, "error", f"Sale order sync failed: {exc}", raw.get("id"))

            offset += self._batch_size

    def _sync_single_order(self, raw_order: dict, raw_lines: list[dict]) -> bool:
        partner = raw_order.get("partner_id")
        customer_odoo_id = partner[0] if isinstance(partner, (list, tuple)) else partner
        customer = self._contacts.get_by_odoo_id(customer_odoo_id)
        if customer is None:
            raise ValueError(f"Customer {customer_odoo_id} not found, sync contacts first")

        lines = [map_sale_order_line(raw_line) for raw_line in raw_lines]

        product_lookup = {}
        for line in lines:
            product = self._products.get_by_odoo_id(line.product_odoo_id)
            if product is None:
                raise ValueError(f"Product {line.product_odoo_id} not found, sync products first")
            product_lookup[line.product_odoo_id] = product

        order = map_sale_order(raw_order, lines)
        _, is_new = self._orders.upsert(order, customer, product_lookup)
        return is_new

    def _group_lines_by_order(self, order_ids: list[int]) -> dict[int, list[dict]]:
        raw_lines = self._odoo.fetch_sale_order_lines(order_ids)
        grouped: dict[int, list[dict]] = {}
        for raw_line in raw_lines:
            order_ref = raw_line.get("order_id")
            order_odoo_id = order_ref[0] if isinstance(order_ref, (list, tuple)) else order_ref
            grouped.setdefault(order_odoo_id, []).append(raw_line)
        return grouped

    def _fetch_with_retry(
        self, fetch_fn, offset: int, limit: int, since: str | None, attempts: int = 3
    ) -> list[dict]:
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                return fetch_fn(offset=offset, limit=limit, since=since)
            except OdooConnectionError as exc:
                last_error = exc
                logger.warning("Odoo fetch attempt %s/%s failed: %s", attempt, attempts, exc)
        raise last_error

    def _log(self, run: SyncRunModel, level: str, message: str, record_odoo_id: int | None = None) -> None:
        entry = SyncLogModel(
            sync_run_id=run.id,
            level=level,
            message=message,
            record_odoo_id=record_odoo_id,
        )
        self._session.add(entry)
        logger.log(logging.ERROR if level == "error" else logging.INFO, message)