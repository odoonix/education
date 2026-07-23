from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, skip: int = 0, limit: int = 50) -> list[Item]:
        return (
            self.db.query(Item)
            .order_by(Item.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, item_id: int) -> Item | None:
        return self.db.get(Item, item_id)

    def create(self, payload: ItemCreate) -> Item:
        item = Item(name=payload.name, description=payload.description)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: Item, payload: ItemUpdate) -> Item:
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Item) -> None:
        self.db.delete(item)
        self.db.commit()
