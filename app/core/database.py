from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    __allow_unmapped__ = True  # Allow legacy type annotations

# Create a database-agnostic JSON type that works with both PostgreSQL (JSONB) and SQLite (JSON)
def get_json_type():
    """Return JSONB for PostgreSQL, JSON for SQLite and other databases."""
    db_url = settings.DATABASE_URL.lower()
    if "postgresql" in db_url or "postgres" in db_url:
        return JSONB
    else:
        return JSON

# Export for use in models
JSONType = get_json_type()

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Import models for metadata
from app.models import all_models  # noqa

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Simple connectivity check
    async with AsyncSessionLocal() as s:
        await s.execute(text("SELECT 1"))