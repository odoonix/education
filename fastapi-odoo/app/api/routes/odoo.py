from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_odoo_service
from app.schemas.odoo import OdooHealth
from app.services.odoo_service import OdooService

router = APIRouter(prefix="/odoo", tags=["odoo"])


@router.get("/health", response_model=OdooHealth)
def odoo_health(service: OdooService = Depends(get_odoo_service)) -> OdooHealth:
    return service.health()
