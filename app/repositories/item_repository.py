from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Item]:
        return self.db.query(Item).offset(skip).limit(limit).all()

    def get_by_id(self, item_id: int) -> Optional[Item]:
        return self.db.query(Item).filter(Item.id == item_id).first()

    def create(self, item_in: ItemCreate) -> Item:
        db_item = Item(
            title=item_in.title,
            description=item_in.description,
            completed=item_in.completed,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update(self, db_item: Item, item_in: ItemUpdate) -> Item:
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def delete(self, db_item: Item) -> None:
        self.db.delete(db_item)
        self.db.commit()
