from app.adapters.sale_order_adapter import SaleOrderAdapter
from app.models import SyncRun
from app.repositories.product_repository import (
    ProductRepository,
)
from app.repositories.sale_order_line_repository import (
    SaleOrderLineRepository,
)
from app.repositories.sale_order_repository import (
    SaleOrderRepository,
)
from app.repositories.sync_repository import SyncRepository


class SaleOrderLineSyncService:
    def __init__(
            self,
            adapter: SaleOrderAdapter,
            product_repository: ProductRepository,
            sale_order_repository: SaleOrderRepository,
            sale_order_line_repository: SaleOrderLineRepository,
            sync_repository: SyncRepository,
    ) -> None:
        self._adapter = adapter
        self._product_repository = product_repository
        self._sale_order_repository = sale_order_repository
        self._sale_order_line_repository = sale_order_line_repository
        self._sync_repository = sync_repository

    def sync(
            self,
            sync_run: SyncRun,
    ) -> int:
        processed_count = 0

        sale_order_lines = (
            self._adapter.fetch_order_lines()
        )

        for sale_order_line_data in sale_order_lines:
            product = (
                self._product_repository.get_by_odoo_id(
                    sale_order_line_data.product_id,
                )
            )

            if product is None:
                raise ValueError(
                    f"Product with Odoo ID "
                    f"{sale_order_line_data.product_id} "
                    f"not found",
                )

            sale_order = (
                self._sale_order_repository.get_by_odoo_id(
                    sale_order_line_data.order_id,
                )
            )

            if sale_order is None:
                raise ValueError(
                    f"Sale order with Odoo ID "
                    f"{sale_order_line_data.order_id} "
                    f"not found",
                )

            existing_sale_order_line = (
                self._sale_order_line_repository
                .get_by_odoo_id(
                    sale_order_line_data.odoo_id,
                )
            )

            if existing_sale_order_line is None:
                self._sale_order_line_repository.create(
                    sale_order_line_data,
                    product.id,
                    sale_order.id,
                )

                action = "created"

            else:
                self._sale_order_line_repository.update(
                    existing_sale_order_line,
                    sale_order_line_data,
                    product.id,
                    sale_order.id,
                )

                action = "updated"

            self._sync_repository.create_log(
                sync_run=sync_run,
                level="INFO",
                entity="sale_order_line",
                action=action,
                record_odoo_id=sale_order_line_data.odoo_id,
                message=(
                    f"Sale Order Line "
                    f"{sale_order_line_data.odoo_id} "
                    f"{action} successfully"
                ),
            )

            processed_count += 1

        sync_run.sale_order_lines_processed = processed_count

        return processed_count
