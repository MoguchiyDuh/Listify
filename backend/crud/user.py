from typing import Optional

from core.security import hash_password, verify_password
from models import User
from sqlalchemy.orm import Session

from .base import CRUDBase, logger

logger = logger.getChild("user")


class CRUDUser(CRUDBase[User]):
    """CRUD operations for users"""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email"""
        logger.debug(f"Getting user by email: {email}")
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username"""
        logger.debug(f"Getting user by username: {username}")
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, username: str, email: str, password: str) -> User:
        """Create new user with hashed password"""
        logger.info(f"Creating user: {username}")

        hashed_password = hash_password(password)

        user = User(username=username, email=email, hashed_password=hashed_password)

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.debug(f"Created user with id: {user.id}")
        return user

    def update(
        self,
        db: Session,
        *,
        user: User,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        """Update user information"""
        logger.info(f"Updating user with id: {user.id}")

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.hashed_password = hash_password(password)

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.debug(f"Updated user with id: {user.id}")
        return user

    def authenticate(
        self, db: Session, *, username: str, password: str
    ) -> Optional[User]:
        """Authenticate user by username and password"""
        logger.debug(f"Authenticating user: {username}")

        user = self.get_by_username(db, username=username)
        if not user:
            logger.warning(f"User not found: {username}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {username}")
            return None

        logger.info(f"User authenticated successfully: {username}")
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active (for future use)"""
        return True


user_crud = CRUDUser(User)
