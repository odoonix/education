from __future__ import annotations

from dataclasses import dataclass

from odoo_sync.application.services.shutdown import ShutdownFlag
from odoo_sync.application.services.sync_service import SyncService
from odoo_sync.config import Settings
from odoo_sync.infrastructure.database.engine import make_session_factory, make_engine
from odoo_sync.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from odoo_sync.infrastructure.logging.configuration import configure_logging
from odoo_sync.infrastructure.odoo.adapter import OdooAdapter
from odoo_sync.infrastructure.odoo.client import OdooClient
from odoo_sync.infrastructure.database.sync_lock import PostgresSyncLock


@dataclass(frozen=True, slots=True)
class Container:
    settings: Settings
    sync_service: SyncService
    shutdown: ShutdownFlag


def build_container() -> Container:
    settings = Settings()
    logger = configure_logging(
        settings.log_level,
        settings.log_format,
    )

    engine = make_engine(settings)
    session_factory = make_session_factory(engine)

    shutdown = ShutdownFlag()
    client = OdooClient(settings, logger)

    sync_lock = PostgresSyncLock(
        engine=engine,
        lock_key=settings.sync_lock_key,
    )

    service = SyncService(
        erp=OdooAdapter(client),
        uow_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
        logger=logger,
        shutdown=shutdown,
        sync_lock=sync_lock,
    )

    return Container(
        settings=settings,
        sync_service=service,
        shutdown=shutdown,
    )
