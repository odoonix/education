from adapters.odoo_adapter import OdooAdapter
from repositories.product_repository import ProductRepository
from mappers.product_mapper import map_product
from services.sync_engine import SyncEngine


def sync_products(session, adapter: OdooAdapter, batch_size: int = 500, shutdown_handler=None) -> dict:
    repo = ProductRepository(session)
    engine = SyncEngine(
        session=session,
        operation_type="products_sync",
        count_fn=adapter.count_products,
        fetch_page_fn=adapter.get_products,
        map_fn=map_product,
        upsert_fn=repo.upsert,
        batch_size=batch_size,
        shutdown_handler=shutdown_handler,
    )
    return engine.run()