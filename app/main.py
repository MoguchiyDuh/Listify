from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import setup_logger
from app.routes import auth, media, search, tracking

logger = setup_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Database tables should be created via Alembic migrations
    # Run: alembic upgrade head
    logger.info("Application started - ensure database migrations are up to date")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent.parent / "static")), name="static")

# Include routers
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


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
