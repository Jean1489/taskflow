import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from app.events import get_redis_client, close_redis_client


# ----------------------------
# Logging configuration
# ----------------------------

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


# ----------------------------
# Lifespan — startup and shutdown
# ----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    #startup
    logger.info("Starting up the application...")
    get_redis_client()  # Initialize Redis client
    logger.info("Redis connection established")

    yield # Run the application

    #shutdown
    logger.info("Shutting down the application...")
    close_redis_client()  # Close Redis client
    logger.info("Redis connection closed")


# ----------------------------
# FastAPI app
# ----------------------------

app = FastAPI(
    title="TaskFlow API",
    description="Event-driven task management API built with FastAPI and Redis",
    version="1.0.0",
    lifespan=lifespan
)

# ----------------------------
# CORS Middleware
# ----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Register routers
# ----------------------------

app.include_router(router)

# ----------------------------
# Health check
# ----------------------------

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "taskflow-api",
        "version": "1.0.0"
    }