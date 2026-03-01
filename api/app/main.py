import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from app.events import get_redis_client, close_redis_client
from app.database import engine, Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting TaskFlow API...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    # Initialize Redis
    get_redis_client()
    logger.info("Redis connection established")

    yield

    # Shutdown
    logger.info("Shutting down TaskFlow API...")
    close_redis_client()
    await engine.dispose()
    logger.info("Connections closed")


app = FastAPI(
    title="TaskFlow API",
    description="Event-driven task management API built with FastAPI and Redis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "taskflow-api",
        "version": "1.0.0"
    }