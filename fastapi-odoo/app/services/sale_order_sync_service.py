from app.adapters.sale_order_adapter import SaleOrderAdapter
from app.models import SyncRun
from app.repositories.contact_repository import (
    ContactRepository,
)
from app.repositories.sale_order_repository import (
    SaleOrderRepository,
)
from app.repositories.sync_repository import SyncRepository


class SaleOrderSyncService:
    def __init__(
        self,
        adapter: SaleOrderAdapter,
        contact_repository: ContactRepository,
        sale_order_repository: SaleOrderRepository,
        sync_repository: SyncRepository,
    ) -> None:
        self._adapter = adapter
        self._contact_repository = contact_repository
        self._sale_order_repository = sale_order_repository
        self._sync_repository = sync_repository

    def sync(
        self,
        sync_run: SyncRun,
    ) -> int:
        processed_count = 0

        sale_orders = self._adapter.fetch_orders()

        for sale_order_data in sale_orders:
            contact = (
                self._contact_repository.get_by_odoo_id(
                    sale_order_data.partner_id,
                )
            )

            if contact is None:
                raise ValueError(
                    f"Contact with Odoo ID "
                    f"{sale_order_data.partner_id} "
                    f"was not found",
                )

            existing_sale_order = (
                self._sale_order_repository.get_by_odoo_id(
                    sale_order_data.odoo_id,
                )
            )

            if existing_sale_order is None:
                self._sale_order_repository.create(
                    sale_order_data,
                    contact.id,
                )

                action = "created"

            else:
                self._sale_order_repository.update(
                    existing_sale_order,
                    sale_order_data,
                    contact.id,
                )

                action = "updated"

            self._sync_repository.create_log(
                sync_run=sync_run,
                level="INFO",
                entity="sale_order",
                action=action,
                record_odoo_id=sale_order_data.odoo_id,
                message=(
                    f"Sale Order {sale_order_data.odoo_id} "
                    f"{action} successfully"
                ),
            )

            processed_count += 1

        sync_run.sale_orders_processed = processed_count

        return processed_count