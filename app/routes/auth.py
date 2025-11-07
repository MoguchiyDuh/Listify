from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.logger import setup_logger
from app.crud import user_crud
from app.models.user import User
from app.routes.deps import create_access_token, get_current_user
from app.schemas import Token, UserCreate, UserLogin, UserResponse

logger = setup_logger("api.auth")

router = APIRouter()
basic_security = HTTPBasic()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Register a new user and set auth cookie"""
    logger.info(f"Registration attempt for username: {user_data.username}")

    if user_crud.get_by_username(db, username=user_data.username):
        logger.warning(f"Username already exists: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    if user_crud.get_by_email(db, email=user_data.email):
        logger.warning(f"Email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = user_crud.create(
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
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    logger.info(f"User registered successfully: {user.username}")
    return user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login and get access token in cookie"""
    logger.info(f"Login attempt for username: {user_data.username}")

    user = user_crud.authenticate(
        db, username=user_data.username, password=user_data.password
    )

    if not user:
        logger.warning(f"Failed login attempt for username: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    logger.info(f"User logged in successfully: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
def login_basic(
    response: Response,
    credentials: HTTPBasicCredentials = Depends(basic_security),
    db: Session = Depends(get_db),
):
    """Login using HTTP Basic Auth (alternative endpoint)"""
    logger.info(f"Basic auth login attempt for username: {credentials.username}")

    user = user_crud.authenticate(
        db, username=credentials.username, password=credentials.password
    )

    if not user:
        logger.warning(f"Failed basic auth for username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
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
