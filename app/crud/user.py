from typing import Optional
from uuid import UUID

from app.core import hash_password, setup_logger
from app.models import User
from app.schemas import UserCreate, UserUpdate
from sqlalchemy import or_
from sqlalchemy.orm import Session

logger = setup_logger(__name__)


class UserCRUD:
    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        logger.debug(f"Creating user: {user_data.username}")

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.debug(f"User created successfully: {user.id}")
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        logger.debug(f"Fetching user by ID: {user_id}")
        user = db.query(User).filter(User.id == user_id).first()

        if user:
            logger.debug(f"User found: {user.username}")
        else:
            logger.debug(f"User not found: {user_id}")

        return user

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        logger.debug(f"Fetching user by username: {username}")
        user = db.query(User).filter(User.username == username).first()

        if user:
            logger.debug(f"User found: {user.id}")
        else:
            logger.debug(f"User not found: {username}")

        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        logger.debug(f"Fetching user by email: {email}")
        user = db.query(User).filter(User.email == email).first()

        if user:
            logger.debug(f"User found: {user.id}")
        else:
            logger.debug(f"User not found: {email}")

        return user

    @staticmethod
    def get_by_username_or_email(db: Session, identifier: str) -> Optional[User]:
        logger.debug(f"Fetching user by username or email: {identifier}")
        user = (
            db.query(User)
            .filter(or_(User.username == identifier, User.email == identifier))
            .first()
        )

        if user:
            logger.debug(f"User found: {user.id}")
        else:
            logger.debug(f"User not found: {identifier}")

        return user

    @staticmethod
    def update(db: Session, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        logger.debug(f"Updating user: {user_id}")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.debug(f"User not found for update: {user_id}")
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        logger.debug(f"User updated successfully: {user.id}")
        return user

    @staticmethod
    def delete(db: Session, user_id: UUID) -> bool:
        logger.debug(f"Deleting user: {user_id}")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.debug(f"User not found for deletion: {user_id}")
            return False

        db.delete(user)
        db.commit()

        logger.debug(f"User deleted successfully: {user_id}")
        return True

    @staticmethod
    def exists(
        db: Session, username: Optional[str] = None, email: Optional[str] = None
    ) -> bool:
        logger.debug(f"Checking user existence - username: {username}, email: {email}")

        query = db.query(User)

        if username and email:
            exists = (
                query.filter(
                    or_(User.username == username, User.email == email)
                ).first()
                is not None
            )
        elif username:
            exists = query.filter(User.username == username).first() is not None
        elif email:
            exists = query.filter(User.email == email).first() is not None
        else:
            exists = False

        logger.debug(f"User exists: {exists}")
        return exists
