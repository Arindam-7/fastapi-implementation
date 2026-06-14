from typing import Generic, Type, TypeVar, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.database import Base

# Declare a generic TypeVar bound to our SQLAlchemy Declarative Base
ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        """
        Generic CRUD repository providing basic data access infrastructure.
        """
        self.model = model
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def create(self, obj_in_data: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.flush()  # Flushes mutations to assign an ID without committing the outer transaction block
        return db_obj