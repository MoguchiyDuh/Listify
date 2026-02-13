from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password
from models import User

from .base import CRUDBase, logger

logger = logger.bind(module="user")


class CRUDUser(CRUDBase[User]):
    """CRUD operations for users"""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email"""
        logger.debug(f"Getting user by email: {email}")
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(
        self, db: AsyncSession, *, username: str
    ) -> Optional[User]:
        """Get user by username"""
        logger.debug(f"Getting user by username: {username}")
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, *, username: str, email: str, password: str
    ) -> User:
        """Create new user with hashed password"""
        logger.info(f"Creating user: {username}")

        hashed_password = hash_password(password)

        user = User(username=username, email=email, hashed_password=hashed_password)

        db.add(user)
        await db.flush()
        await db.commit()
        await db.refresh(user)

        logger.debug(f"Created user with id: {user.id}")
        return user

    async def update(
        self,
        db: AsyncSession,
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
        await db.flush()
        await db.commit()
        await db.refresh(user)

        logger.debug(f"Updated user with id: {user.id}")
        return user

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        """Authenticate user by username/email and password"""
        logger.debug(f"Authenticating user: {username}")

        # Try to find by username
        user = await self.get_by_username(db, username=username)
        if not user:
            # Try to find by email
            user = await self.get_by_email(db, email=username)

        if not user:
            logger.warning(f"User not found with identifier: {username}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {user.username}")
            return None

        logger.info(f"User authenticated successfully: {user.username}")
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active (for future use)"""
        return True


user_crud = CRUDUser(User)
