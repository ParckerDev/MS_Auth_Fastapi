from sqlalchemy import Integer, func, DateTime
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from app.core.utils import camel_case_to_snake_case as cctsc




class Base(DeclarativeBase):
    __abstract__ = True


    @declared_attr.directive
    def __tablename__(cls):
        return f'{cctsc(cls.__name__)}'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )