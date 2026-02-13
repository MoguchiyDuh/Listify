from contextlib import asynccontextmanager
from pathlib import Path

import asyncio
import secrets
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.cache import cache
from core.config import settings
from core.database import AsyncSessionLocal, get_db
from core.exceptions import ListifyException, Unauthorized
from core.limiter import limiter
from core.logger import setup_logger, get_logger
from crud import media_crud
from routes import auth, media, search, tracking

# Initialize logging
setup_logger()
logger = get_logger("main")


async def periodic_media_cleanup():
    """Periodic task to clean up orphaned media"""
    # Wait a bit before starting the first cleanup to let the app initialize
    await asyncio.sleep(60)
    while True:
        try:
            logger.info("Starting periodic orphaned media cleanup background task")
            async with AsyncSessionLocal() as db:
                deleted_count = await media_crud.cleanup_orphaned_media(db)
                logger.info(f"Periodic cleanup completed. Deleted {deleted_count} items.")
        except Exception as e:
            logger.error(f"Error in periodic media cleanup task: {e}")

        # Sleep for 24 hours
        await asyncio.sleep(24 * 60 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    static_dir = Path(__file__).parent / "static"
    images_dir = static_dir / "images"
    static_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    logger.debug(f"Ensured directories exist: {static_dir}, {images_dir}")

    logger.info("Application started - ensure database migrations are up to date")

    await cache.connect()

    # Start background tasks
    cleanup_task = asyncio.create_task(periodic_media_cleanup())

    yield

    # Cleanup background tasks
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.debug("Background cleanup task cancelled")

    await cache.disconnect()
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    """Simple CSRF protection middleware using double-submit cookie pattern"""
    if request.method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
        response: Response = await call_next(request)
        # Set CSRF cookie if not present
        if not request.cookies.get("csrf_token"):
            csrf_token = secrets.token_urlsafe(32)
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,  # Frontend needs to read this
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
            )
        return response

    # For mutation requests, verify token
    csrf_token_cookie = request.cookies.get("csrf_token")
    csrf_token_header = request.headers.get("X-CSRF-Token")

    if not csrf_token_cookie or not csrf_token_header or csrf_token_cookie != csrf_token_header:
        logger.warning(f"CSRF verification failed for {request.method} {request.url.path}")
        return JSONResponse(
            status_code=403,
            content={"detail": "CSRF token missing or invalid"},
        )

    return await call_next(request)


@app.exception_handler(ListifyException)
async def listify_exception_handler(request: Request, exc: ListifyException):
    """Handle custom Listify exceptions"""
    logger.warning(
        "listify_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.middleware("http")
async def global_exception_middleware(request: Request, call_next):
    """Catch-all middleware for unhandled exceptions"""
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception(
            "unhandled_exception",
            error=str(e),
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent / "static")),
    name="static",
)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
app.include_router(search.router, prefix="/api/search", tags=["search"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/api/live")
async def live_check():
    """Liveness check endpoint"""
    return {"status": "alive"}


@app.get("/api/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check endpoint - verifies DB and Redis connectivity"""
    try:
        # Check DB
        await db.execute(text("SELECT 1"))
        # Check Redis
        await cache.ping()
        return {"status": "ready"}
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "detail": "Infrastructure connection failed"},
        )


@app.get("/health")
async def health():
    """Health check endpoint (legacy)"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
