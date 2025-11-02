from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.core.config import settings

database_url = settings.DATABASE_URL
normalized_url = database_url.lower()

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if normalized_url.startswith("sqlite"):
    # SQLite does not support SSL parameters such as ``sslmode``.
    # Provide only the arguments it understands to avoid connection errors.
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(database_url, **engine_kwargs)
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