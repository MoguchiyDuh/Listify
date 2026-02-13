from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Cookie, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.exceptions import Unauthorized
from crud import user_crud
from models import User

from .base import logger

logger = logger.bind(module="deps")

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    logger.debug(f"Created access token for user: {data.get('sub')}")
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Failed to decode token: {e}")
        raise Unauthorized("Could not validate credentials")


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from cookie or bearer token"""
    # Try to get token from cookie first, then from bearer
    token = access_token
    if not token and credentials:
        token = credentials.credentials

    if not token:
        logger.warning("No token provided in cookie or header")
        raise Unauthorized("Not authenticated")

    payload = decode_token(token)
    username: str = payload.get("sub")

    if username is None:
        logger.warning("Token payload missing 'sub' field")
        raise Unauthorized("Could not validate credentials")

    user = await user_crud.get_by_username(db, username=username)
    if user is None:
        logger.warning(f"User not found: {username}")
        raise Unauthorized("User not found")

    logger.debug(f"Authenticated user: {username}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (for future use with user activation)"""
    return current_user
