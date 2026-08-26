from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class ItemResponse(ItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
