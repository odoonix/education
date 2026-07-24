import logging

from app.mapping.mappers import (
    extract_order_odoo_id,
    extract_partner_odoo_id,
    extract_product_odoo_id,
    map_sale_order,
    map_sale_order_line,
)
from app.odoo_client.client import OdooClient
from app.repositories.contact_repository import ContactRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_order_line_repository import SaleOrderLineRepository
from app.repositories.sale_order_repository import SaleOrderRepository
from app.services.stats import SyncStats
from app.services.sync_logger import SyncRunLogger

logger = logging.getLogger(__name__)

SALE_ORDER_FIELDS = ["id", "name", "partner_id", "date_order", "state", "amount_total"]
SALE_ORDER_LINE_FIELDS = [
    "id",
    "order_id",
    "product_id",
    "product_uom_qty",
    "price_unit",
    "price_subtotal",
]
SALE_ORDER_DOMAIN: list = []

SALE_ORDER_LINE_DOMAIN: list = [("display_type", "=", False)]


class SaleOrderSyncService:
    def __init__(
        self,
        odoo_client: OdooClient,
        sale_order_repository: SaleOrderRepository,
        sale_order_line_repository: SaleOrderLineRepository,
        contact_repository: ContactRepository,
        product_repository: ProductRepository,
    ):
        self.odoo_client = odoo_client
        self.sale_order_repository = sale_order_repository
        self.sale_order_line_repository = sale_order_line_repository
        self.contact_repository = contact_repository
        self.product_repository = product_repository

    def sync(self, sync_run_logger: SyncRunLogger) -> SyncStats:
        total = SyncStats()
        total.merge(self._sync_orders(sync_run_logger))
        total.merge(self._sync_order_lines(sync_run_logger))
        return total


    def _sync_orders(self, sync_run_logger: SyncRunLogger) -> SyncStats:
        stats = SyncStats()

        for raw in self.odoo_client.iter_all(
            "sale.order", SALE_ORDER_DOMAIN, SALE_ORDER_FIELDS, batch_size=100
        ):
            stats.fetched += 1
            odoo_id = raw["id"]
            try:
                partner_odoo_id = extract_partner_odoo_id(raw)
                customer_internal_id = None
                if partner_odoo_id is not None:
                    contact = self.contact_repository.get_by_odoo_id(partner_odoo_id)
                    if contact is not None:
                        customer_internal_id = contact.id
                    else:
                        sync_run_logger.log_warning(
                            f"Partner with odoo_id={partner_odoo_id} not found in local database for order "
                            f"odoo_id={odoo_id}; order will be saved without customer.",
                            entity_type="sale_order",
                            entity_odoo_id=odoo_id,
                        )

                data = map_sale_order(raw, customer_internal_id)
                _, created = self.sale_order_repository.upsert(odoo_id, data)
                if created:
                    stats.created += 1
                else:
                    stats.updated += 1
            except Exception as exc: 
                stats.failed += 1
                logger.exception(f"error processing order with odoo_id={odoo_id}")
                sync_run_logger.log_error("sale_order", odoo_id, str(exc))
                continue

        return stats


    def _sync_order_lines(self, sync_run_logger: SyncRunLogger) -> SyncStats:
        stats = SyncStats()

        for raw in self.odoo_client.iter_all(
            "sale.order.line",
            SALE_ORDER_LINE_DOMAIN,
            SALE_ORDER_LINE_FIELDS,
            batch_size=200,
        ):
            stats.fetched += 1
            odoo_id = raw["id"]
            try:
                order_odoo_id = extract_order_odoo_id(raw)
                sale_order = (
                    self.sale_order_repository.get_by_odoo_id(order_odoo_id)
                    if order_odoo_id is not None
                    else None
                )
                if sale_order is None:
                    stats.failed += 1
                    sync_run_logger.log_error(
                        "sale_order_line",
                        odoo_id,
                        f"Parent order with odoo_id={order_odoo_id} not found; "
                        "this line has been skipped.",
                    )
                    continue

                product_odoo_id = extract_product_odoo_id(raw)
                product_internal_id = None
                if product_odoo_id is not None:
                    product = self.product_repository.get_by_odoo_id(product_odoo_id)
                    if product is not None:
                        product_internal_id = product.id
                    else:
                        sync_run_logger.log_warning(
                            f"Product with odoo_id={product_odoo_id} not found for line "
                            f"odoo_id={odoo_id}; saving without product association.",
                            entity_type="sale_order_line",
                            entity_odoo_id=odoo_id,
                        )
                        

                data = map_sale_order_line(raw, sale_order.id, product_internal_id)
                _, created = self.sale_order_line_repository.upsert(odoo_id, data)
                if created:
                    stats.created += 1
                else:
                    stats.updated += 1
            except Exception as exc:
                stats.failed += 1
                logger.exception(f"error processing line with odoo_id={odoo_id}")
                sync_run_logger.log_error("sale_order_line", odoo_id, str(exc))
                continue

        return stats
