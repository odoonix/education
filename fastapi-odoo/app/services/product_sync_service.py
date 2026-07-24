from app.adapters.product_adapter import ProductAdapter
from app.models import SyncRun
from app.repositories.product_repository import (
    ProductRepository,
)
from app.repositories.sync_repository import SyncRepository


class ProductSyncService:
    def __init__(
            self,
            adapter: ProductAdapter,
            product_repository: ProductRepository,
            sync_repository: SyncRepository,
    ) -> None:
        self._adapter = adapter
        self._product_repository = product_repository
        self._sync_repository = sync_repository

    def sync(
            self,
            sync_run: SyncRun,
    ) -> int:
        processed_count = 0

        products = self._adapter.fetch_products()

        for product_data in products:
            existing_product = (
                self._product_repository.get_by_odoo_id(
                    product_data.odoo_id,
                )
            )

            if existing_product is None:
                self._product_repository.create(
                    product_data,
                )

                action = "created"

            else:
                self._product_repository.update(
                    existing_product,
                    product_data,
                )

                action = "updated"

            self._sync_repository.create_log(
                sync_run=sync_run,
                level="INFO",
                entity="product",
                action=action,
                record_odoo_id=product_data.odoo_id,
                message=(
                    f"Product {product_data.odoo_id} "
                    f"{action} successfully"
                ),
            )

            processed_count += 1

        sync_run.products_processed = processed_count

        return processed_count
