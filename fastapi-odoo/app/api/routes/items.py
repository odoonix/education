from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_item_service
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemRead])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: ItemService = Depends(get_item_service),
) -> list[ItemRead]:
    return service.list_items(skip=skip, limit=limit)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    service: ItemService = Depends(get_item_service),
) -> ItemRead:
    return service.create_item(payload)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
) -> ItemRead:
    return service.get_item(item_id)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    service: ItemService = Depends(get_item_service),
) -> ItemRead:
    return service.update_item(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
) -> None:
    service.delete_item(item_id)


@router.post("/{item_id}/sync-odoo", response_model=ItemRead)
def sync_item_to_odoo(
    item_id: int,
    email: str | None = None,
    service: ItemService = Depends(get_item_service),
) -> ItemRead:
    """Create a matching res.partner in Odoo and store its id on the item."""
    return service.sync_item_to_odoo(item_id, email=email)
