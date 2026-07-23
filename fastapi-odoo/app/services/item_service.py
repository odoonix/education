from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.integrations.odoo_client import OdooClient, OdooClientError
from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate
from app.schemas.odoo import OdooPartnerCreate


class ItemService:
    def __init__(self, db: Session, odoo: OdooClient | None = None) -> None:
        self.repo = ItemRepository(db)
        self.odoo = odoo or OdooClient()

    def list_items(self, skip: int = 0, limit: int = 50) -> list[Item]:
        return self.repo.list(skip=skip, limit=limit)

    def get_item(self, item_id: int) -> Item:
        item = self.repo.get(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return item

    def create_item(self, payload: ItemCreate) -> Item:
        return self.repo.create(payload)

    def update_item(self, item_id: int, payload: ItemUpdate) -> Item:
        item = self.get_item(item_id)
        return self.repo.update(item, payload)

    def delete_item(self, item_id: int) -> None:
        item = self.get_item(item_id)
        self.repo.delete(item)

    def sync_item_to_odoo(self, item_id: int, email: str | None = None) -> Item:
        item = self.get_item(item_id)
        try:
            partner = self.odoo.create_partner(
                OdooPartnerCreate(name=item.name, email=email)
            )
        except OdooClientError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

        return self.repo.update(item, ItemUpdate(odoo_partner_id=partner.id))
