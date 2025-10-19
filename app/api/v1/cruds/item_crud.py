from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


from app.core.schemas.item_schema import ItemCreate, ItemUpdate
from app.core.models.item_model import Item




async def get_items(session: AsyncSession) -> List[Item]:
    """
    Возвращает список всех Item (ORM объекты).
    session: AsyncSession — получаем в роутере через Depends(db_helper.get_session)
    """
    result = await session.scalars(select(Item))
    items: List[Item] = list(result.all())
    return items


async def get_item_by_id(item_id: int, session: AsyncSession) -> Optional[Item]:
    """
    Возвращает объект Item по id или None, если не найден.
    """
    result = await session.scalars(select(Item).where(Item.id == item_id))
    return result.first()


async def item_create(item: ItemCreate, session: AsyncSession, *, hash_password: bool = False) -> Item:
    """
    Создаёт Item из Pydantic-схемы ItemCreate.
    """
    data = item.model_dump()
    instance = Item(**data)
    session.add(instance)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    await session.refresh(instance)
    return instance


async def item_update(item_id: int, item_in: ItemUpdate, session: AsyncSession, *, hash_password: bool = False) -> Optional[Item]:
    """
    Обновляет существующий Item.
    - item_in: Pydantic-схема ItemUpdate.
    - Возвращает обновлённый объект или None, если не найден.
    """
    obj = await get_item_by_id(item_id, session)
    if not obj:
        return None

    data = item_in.model_dump(exclude_unset=True)
    
    for field, value in data.items():
        setattr(obj, field, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise

    await session.refresh(obj)
    return obj


async def item_delete(item_id: int, session: AsyncSession) -> Optional[Item]:
    """
    Удаляет Item по id. Возвращает удалённый объект (до удаления) или None.
    """
    obj = await get_item_by_id(item_id, session)
    if not obj:
        return None

    await session.delete(obj)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return obj
