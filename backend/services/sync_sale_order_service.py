from adapters.odoo_adapter import OdooAdapter
from repositories.sale_order_repository import SaleOrderRepository
from mappers.sale_order_mapper import map_sale_order
from services.sync_engine import SyncEngine


def sync_sale_orders(session, adapter: OdooAdapter, batch_size: int = 200, shutdown_handler=None) -> dict:
    repo = SaleOrderRepository(session)
    engine = SyncEngine(
        session=session,
        operation_type="sale_orders_sync",
        count_fn=adapter.count_sale_orders,
        fetch_page_fn=adapter.get_sale_orders,
        map_fn=map_sale_order,
        upsert_fn=repo.upsert,
        batch_size=batch_size,
        shutdown_handler=shutdown_handler,
    )
    return engine.run()