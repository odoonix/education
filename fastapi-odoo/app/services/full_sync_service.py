from app.models.sync import SyncRun
from app.repositories.sync_repository import SyncRepository
from app.services.contact_sync_service import ContactSyncService
from app.services.product_sync_service import ProductSyncService
from app.services.sale_order_line_sync_service import (
    SaleOrderLineSyncService,
)
from app.services.sale_order_sync_service import (
    SaleOrderSyncService,
)


class FullSyncService:
    def __init__(
            self,
            sync_repository: SyncRepository,
            contact_sync_service: ContactSyncService,
            product_sync_service: ProductSyncService,
            sale_order_sync_service: SaleOrderSyncService,
            sale_order_line_sync_service: (
                    SaleOrderLineSyncService
            ),
    ) -> None:
        self._sync_repository = sync_repository
        self._contact_sync_service = (
            contact_sync_service
        )
        self._product_sync_service = (
            product_sync_service
        )
        self._sale_order_sync_service = (
            sale_order_sync_service
        )
        self._sale_order_line_sync_service = (
            sale_order_line_sync_service
        )

    def sync(self) -> SyncRun:
        sync_run = self._sync_repository.create_run()

        try:
            self._contact_sync_service.sync(sync_run)
            self._product_sync_service.sync(sync_run)
            self._sale_order_sync_service.sync(sync_run)
            self._sale_order_line_sync_service.sync(sync_run)

            self._sync_repository.complete_run(sync_run)
            return sync_run

        except Exception as error:
            self._sync_repository.fail_run(
                sync_run=sync_run,
                error_message=str(error),
            )

            raise
