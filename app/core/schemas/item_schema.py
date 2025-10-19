from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints, ConfigDict

# Применяем StringConstraints для строковых полей:
# - strip_whitespace убирает пробелы по краям
# - min_length / max_length задают ограничения длины
NameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
OptNameStr = Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]]


class ItemBase(BaseModel):
    """
    Базовая схема с общими полями для Item.
    """
    name: NameStr = Field(..., description="Название предмета")
    description: Optional[str] = Field(None, description="Описание")
    price: Optional[float] = Field(None, ge=0, description="Цена")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "Example Item",
                "description": "Краткое описание предмета",
                "price": 9.99,
            }
        }
    )


class ItemCreate(ItemBase):
    """Схема для создания Item (наследует ItemBase)."""
    pass


class ItemUpdate(BaseModel):
    """
    Схема для частичного обновления Item.
    Все поля опциональны — используйте .dict(exclude_unset=True) при передаче в CRUD.
    """
    name: OptNameStr = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "Updated name",
                "description": "Updated description",
                "price": 12.5,
            }
        }
    )


class ItemOut(ItemBase):
    """
    Схема для вывода Item клиенту.
    from_attributes=True позволяет возвращать ORM-объекты напрямую.
    """
    id: int = Field(..., description="ID записи")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Example Item",
                "description": "Краткое описание предмета",
                "price": 9.99,
                "created_at": "2025-09-05T12:00:00",
                "updated_at": "2025-09-05T12:30:00",
            }
        }
    )
# Дополнительные схемы (например, для списков с пагинацией) можно добавить здесь.
class ItemsList(BaseModel):
    """
    Схема для ответа со списком Item с пагинацией.
    """
    total: int = Field(..., description="Общее количество Item")
    items: list[ItemOut] = Field(..., description="Список Item на текущей странице")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 100,
                "items": [
                    {
                        "id": 1,
                        "name": "Example Item 1",
                        "description": "Описание 1",
                        "price": 9.99,
                        "created_at": "2025-09-05T12:00:00",
                        "updated_at": "2025-09-05T12:30:00",
                    },
                    {
                        "id": 2,
                        "name": "Example Item 2",
                        "description": "Описание 2",
                        "price": 19.99,
                        "created_at": "2025-09-05T13:00:00",
                        "updated_at": "2025-09-05T13:30:00",
                    },
                ],
            }
        }
    )