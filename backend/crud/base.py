from typing import Any, Generic, List, Optional, Type, TypeVar

from core.database import Base
from core.logger import setup_logger
from sqlalchemy.orm import Session

logger = setup_logger("crud")

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """Base CRUD operations"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        logger.debug(f"Getting {self.model.__name__} with id: {id}")
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records"""
        logger.debug(
            f"Getting {self.model.__name__} records (skip: {skip}, limit: {limit})"
        )
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: dict) -> ModelType:
        """Create a new record"""
        logger.info(f"Creating {self.model.__name__}")
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.debug(f"Created {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Update a record"""
        logger.info(f"Updating {self.model.__name__} with id: {db_obj.id}")
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.debug(f"Updated {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    def delete(self, db: Session, *, id: Any) -> bool:
        """Delete a record"""
        logger.info(f"Deleting {self.model.__name__} with id: {id}")
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
            logger.debug(f"Deleted {self.model.__name__} with id: {id}")
            return True
        logger.warning(f"{self.model.__name__} not found with id: {id}")
        return False
