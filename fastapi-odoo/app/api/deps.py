from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.odoo_client import OdooClient, get_odoo_client
from app.services.item_service import ItemService
from app.services.odoo_service import OdooService
from app.services.sync_service import SyncService


def get_item_service(db: Session = Depends(get_db)) -> Generator[ItemService, None, None]:
    yield ItemService(db=db)


def get_odoo_service(
    client: OdooClient = Depends(get_odoo_client),
) -> Generator[OdooService, None, None]:
    yield OdooService(client=client)


def get_sync_service(
    db: Session = Depends(get_db),
    client: OdooClient = Depends(get_odoo_client),
) -> Generator[SyncService, None, None]:
    yield SyncService(db=db, odoo=client)
