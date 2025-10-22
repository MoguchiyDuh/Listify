from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import setup_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = setup_logger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Listify",
    debug=settings.DEBUG,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message": "Listify API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
