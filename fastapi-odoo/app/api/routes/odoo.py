from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_odoo_service
from app.schemas.odoo import OdooHealth, OdooPartnerCreate, OdooPartnerRead
from app.services.odoo_service import OdooService

router = APIRouter(prefix="/odoo", tags=["odoo"])


@router.get("/health", response_model=OdooHealth)
def odoo_health(service: OdooService = Depends(get_odoo_service)) -> OdooHealth:
    return service.health()


@router.get("/partners", response_model=list[OdooPartnerRead])
def list_partners(
    limit: int = Query(20, ge=1, le=100),
    service: OdooService = Depends(get_odoo_service),
) -> list[OdooPartnerRead]:
    try:
        return service.list_partners(limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/partners", response_model=OdooPartnerRead, status_code=status.HTTP_201_CREATED)
def create_partner(
    payload: OdooPartnerCreate,
    service: OdooService = Depends(get_odoo_service),
) -> OdooPartnerRead:
    try:
        return service.create_partner(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
