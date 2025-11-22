from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Base
from core.logger import setup_logger

logger = setup_logger("crud")

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """Base CRUD operations"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        logger.debug(f"Getting {self.model.__name__} with id: {id}")
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records"""
        logger.debug(
            f"Getting {self.model.__name__} records (skip: {skip}, limit: {limit})"
        )
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, *args, obj_in: dict, **kwargs
    ) -> ModelType:
        """Create a new record"""
        logger.info(f"Creating {self.model.__name__}")
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.debug(f"Created {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: dict
    ) -> ModelType:
        """Update a record"""
        logger.info(f"Updating {self.model.__name__} with id: {db_obj.id}")
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.debug(f"Updated {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> bool:
        """Delete a record"""
        logger.info(f"Deleting {self.model.__name__} with id: {id}")
        obj = await db.get(self.model, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            logger.debug(f"Deleted {self.model.__name__} with id: {id}")
            return True
        logger.warning(f"{self.model.__name__} not found with id: {id}")
        return False
