# src/db.py

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from utils.config import DATABASE_URL

# 1) Single AsyncEngine for the whole app
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # for SQLite
)

# 2) Single session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3) Single Base for all your models
Base = declarative_base()

async def init_db():
    """Create all tables in data/users.db."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
