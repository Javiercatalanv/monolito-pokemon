from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.services.item_service import ItemService

router = APIRouter()


def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    return ItemService(db)


@router.get("", response_model=List[ItemResponse], summary="Listar todos los items")
def list_items(
    skip: int = 0,
    limit: int = 100,
    service: ItemService = Depends(get_item_service)
):
    """
    Retorna la lista de items registrados.
    """
    return service.list_items(skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemResponse, summary="Obtener un item por ID")
def get_item(
    item_id: int,
    service: ItemService = Depends(get_item_service)
):
    """
    Retorna el detalle de un item especifico.
    """
    return service.get_item(item_id)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo item")
def create_item(
    item_in: ItemCreate,
    service: ItemService = Depends(get_item_service)
):
    """
    Crea un nuevo item en el sistema.
    """
    return service.create_item(item_in)


@router.put("/{item_id}", response_model=ItemResponse, summary="Actualizar un item existente")
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    service: ItemService = Depends(get_item_service)
):
    """
    Actualiza parcialmente o totalmente un item.
    """
    return service.update_item(item_id, item_in)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un item")
def delete_item(
    item_id: int,
    service: ItemService = Depends(get_item_service)
):
    """
    Elimina un item por su ID.
    """
    service.delete_item(item_id)
    return None
