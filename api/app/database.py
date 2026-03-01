from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# ----------------------------
# Database URL
# ----------------------------
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://taskflow:taskflow123@localhost:5432/taskflow"
)


# ----------------------------
# Engine — the connection pool
# ----------------------------
engine = create_async_engine(
    DATABASE_URL, 
    echo=True, 
    pool_size=10, 
    max_overflow=20
)


# ----------------------------
# Session factory
# ----------------------------
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ----------------------------
# Base class for models
# ----------------------------

class Base(DeclarativeBase):
    pass

# ----------------------------
# Dependency — get DB session
# ----------------------------

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
