from adapters.odoo_adapter import OdooAdapter
from repositories.sale_order_line_repository import SaleOrderLineRepository
from mappers.sale_order_line_mapper import map_sale_order_line
from services.sync_engine import SyncEngine


def sync_sale_order_lines(session, adapter: OdooAdapter, batch_size: int = 200, shutdown_handler=None) -> dict:
    repo = SaleOrderLineRepository(session)
    engine = SyncEngine(
        session=session,
        operation_type="sale_order_lines_sync",
        count_fn=adapter.count_sale_order_lines,
        fetch_page_fn=adapter.get_sale_order_lines,
        map_fn=map_sale_order_line,
        upsert_fn=repo.upsert,
        batch_size=batch_size,
        shutdown_handler=shutdown_handler,
    )
    return engine.run()