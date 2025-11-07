import uvicorn

from app.core.config import settings

uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info" if not settings.DEBUG else "debug",
)
