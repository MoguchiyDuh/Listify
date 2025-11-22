from datetime import timedelta

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.exceptions import AlreadyExists, Unauthorized
from crud import user_crud
from models import User
from schemas import Token, UserCreate, UserLogin, UserResponse

from .base import logger
from .deps import create_access_token, get_current_user

logger = logger.getChild("auth")

router = APIRouter()
basic_security = HTTPBasic()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate, response: Response, db: AsyncSession = Depends(get_db)
):
    """Register a new user and set auth cookie"""
    logger.info(f"Registration attempt for username: {user_data.username}")

    if await user_crud.get_by_username(db, username=user_data.username):
        logger.warning(f"Username already exists: {user_data.username}")
        raise AlreadyExists("Username", user_data.username)

    if await user_crud.get_by_email(db, email=user_data.email):
        logger.warning(f"Email already exists: {user_data.email}")
        raise AlreadyExists("Email", user_data.email)

    user = await user_crud.create(
        db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )

    logger.info(f"User registered successfully: {user.username}")
    return user


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
):
    """Login and get access token in cookie"""
    logger.info(f"Login attempt for username: {user_data.username}")

    user = await user_crud.authenticate(
        db, username=user_data.username, password=user_data.password
    )

    if not user:
        logger.warning(f"Failed login attempt for username: {user_data.username}")
        raise Unauthorized("Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )

    logger.info(f"User logged in successfully: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_basic(
    response: Response,
    credentials: HTTPBasicCredentials = Depends(basic_security),
    db: AsyncSession = Depends(get_db),
):
    """Login using HTTP Basic Auth (alternative endpoint)"""
    logger.info(f"Basic auth login attempt for username: {credentials.username}")

    user = await user_crud.authenticate(
        db, username=credentials.username, password=credentials.password
    )

    if not user:
        logger.warning(f"Failed basic auth for username: {credentials.username}")
        raise Unauthorized("Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )

    logger.info(f"User logged in via basic auth: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    """Logout by clearing cookie"""
    response.delete_cookie(key="access_token")
    logger.info("User logged out")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user
