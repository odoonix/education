from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_odoo_service, get_sync_service
from app.repositories.contact_repository import ContactRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_order_repository import SaleOrderRepository
from app.schemas.sync import (
    ContactRead,
    ProductRead,
    SaleOrderRead,
    SyncEntityResult,
    SyncResult,
)
from app.services.odoo_service import OdooService
from app.services.sync_service import SyncService

router = APIRouter(tags=["sync"])


@router.post("/sync", response_model=SyncResult)
def sync_all_from_odoo(service: SyncService = Depends(get_sync_service)) -> SyncResult:
    """Pull contacts, products, sale orders and lines from Odoo (create or update)."""
    try:
        return service.sync_all()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/sync/contacts", response_model=SyncEntityResult)
def sync_contacts(service: SyncService = Depends(get_sync_service)) -> SyncEntityResult:
    try:
        return service.sync_contacts()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/sync/products", response_model=SyncEntityResult)
def sync_products(service: SyncService = Depends(get_sync_service)) -> SyncEntityResult:
    try:
        return service.sync_products()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/sync/sale-orders", response_model=SyncResult)
def sync_sale_orders(service: SyncService = Depends(get_sync_service)) -> SyncResult:
    try:
        return service.sync_sale_orders()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/contacts", response_model=list[ContactRead])
def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ContactRead]:
    return ContactRepository(db).list(skip=skip, limit=limit)


@router.get("/products", response_model=list[ProductRead])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return ProductRepository(db).list(skip=skip, limit=limit)


@router.get("/sale-orders", response_model=list[SaleOrderRead])
def list_sale_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[SaleOrderRead]:
    return SaleOrderRepository(db).list(skip=skip, limit=limit)


@router.get("/sale-orders/{order_id}", response_model=SaleOrderRead)
def get_sale_order(order_id: int, db: Session = Depends(get_db)) -> SaleOrderRead:
    order = SaleOrderRepository(db).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale order not found")
    return order


@router.post("/odoo/seed-demo")
def seed_odoo_demo(odoo_service: OdooService = Depends(get_odoo_service)) -> dict:
    """Create sample contacts, products, and sale orders in Odoo."""
    try:
        return odoo_service.seed_demo_data()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
