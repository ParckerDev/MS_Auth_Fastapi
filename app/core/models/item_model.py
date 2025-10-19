from typing import Optional
from decimal import Decimal

from sqlalchemy import Integer, String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class Item(Base):

    # Первичный ключ
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Название — обязательное строковое поле, индекс для ускорения поиска
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True, unique=True)

    # Описание — текстовое поле, допускает NULL
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Цена — Decimal/NUMERIC(12,2). Подходит для хранения денежных значений.
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    

    def __repr__(self) -> str:
        return f"<Item id={self.id} name={self.name!r} price={self.price}>"
