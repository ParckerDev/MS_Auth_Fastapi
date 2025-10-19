from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.db_helper import db_helper
from app.core.schemas.item_schema import ItemCreate, ItemUpdate, ItemOut
from app.api.v1.cruds.item_crud import (
    get_items,
    get_item_by_id,
    item_create,
    item_update,
    item_delete,
)

router = APIRouter(prefix="/item", tags=["ITEM"])

# Зависимость для получения асинхронной сессии в роутерах.
# В CRUD-функциях мы принимаем AsyncSession напрямую (без Depends).
SessionDep = Annotated[AsyncSession, Depends(db_helper.get_session)]




@router.get("/", response_model=List[ItemOut])
async def route_get_items(session: SessionDep):
    """
    Получить все Item.
    - session: AsyncSession, получаем через Depends.
    - Возвращает список ItemOut (Pydantic) — FastAPI выполнит автоприведение через response_model.
    """
    return await get_items(session)


@router.get("/{item_id}", response_model=ItemOut)
async def route_get_item(item_id: int, session: SessionDep):
    """
    Получить один Item по id.
    - Если объект не найден, вернуть 404.
    """
    item = await get_item_by_id(item_id, session)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def route_create_item(item: ItemCreate, session: SessionDep):
    """
    Создать новый Item.
    - item: Pydantic-схема ItemCreate, FastAPI валидирует входные данные.
    - При конфликте уникальности (IntegrityError) возвращаем 409.
    - Если создание по каким-то причинам не вернуло объект — возвращаем 400.
    """
    try:
        created = await item_create(item, session)
    except IntegrityError:
        # Конфликт уникальности (например, дублирующийся уникальный индекс)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict")
    if not created:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create item")
    return created


@router.patch("/{item_id}", response_model=ItemOut)
async def route_update_item(item_id: int, item: ItemUpdate, session: SessionDep):
    """
    Частичное обновление Item.
    - item: Pydantic-схема ItemUpdate; в вызове используется exclude_unset=True внутри CRUD.
    - При конфликте уникальности возвращаем 409.
    - Если объект не найден — 404.
    """
    try:
        updated = await item_update(item_id, item, session)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict")
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return updated


@router.delete("/{item_id}", response_model=ItemOut)
async def route_delete_item(item_id: int, session: SessionDep):
    """
    Удалить Item по id.
    - Если объект не найден — 404.
    - Возвращает удалённый объект (до удаления) в формате ItemOut.
    """
    deleted = await item_delete(item_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return deleted