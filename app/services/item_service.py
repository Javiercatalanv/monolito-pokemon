from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db: Session):
        self.repository = ItemRepository(db)

    def list_items(self, skip: int = 0, limit: int = 100) -> list[Item]:
        return self.repository.get_all(skip=skip, limit=limit)

    def get_item(self, item_id: int) -> Item:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Item con id {item_id} no encontrado"
            )
        return item

    def create_item(self, item_in: ItemCreate) -> Item:
        return self.repository.create(item_in)

    def update_item(self, item_id: int, item_in: ItemUpdate) -> Item:
        item = self.get_item(item_id)
        return self.repository.update(item, item_in)

    def delete_item(self, item_id: int) -> None:
        item = self.get_item(item_id)
        self.repository.delete(item)
