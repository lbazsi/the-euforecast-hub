import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import make_url
from app.core.config import settings

database_url = settings.DATABASE_URL
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

url_obj = make_url(database_url)
drivername = url_obj.drivername.lower()

# Normalise query parameters so we can safely mutate them.
original_query_params = dict(url_obj.query.items())
query_params = dict(original_query_params)
sslmode_value = None

# ``sslmode`` is not universally supported.  Capture it so we can either
# translate it (for asyncpg) or drop it (for SQLite/other drivers).
for key in list(query_params.keys()):
@@ -62,26 +64,47 @@ class Base(DeclarativeBase):

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


async def safe_init() -> None:
    """Ensure database tables exist when the module is imported."""
    try:
        await init_models()
        print("✅ Database tables initialized successfully.")
    except Exception as exc:
        print(f"⚠️ Database initialization skipped or failed: {exc}")


def _schedule_safe_init() -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(safe_init())
    else:
        loop.create_task(safe_init())


_schedule_safe_init()