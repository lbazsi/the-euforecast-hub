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
    if key.lower() == "sslmode":
        sslmode_value = query_params.pop(key)

if sslmode_value is not None:
    if drivername.startswith("postgresql+asyncpg"):
        # ``asyncpg`` expects a boolean ``ssl`` argument rather than ``sslmode``.
        ssl_normalised = str(sslmode_value).lower()
        connect_args = engine_kwargs.setdefault("connect_args", {})

        if ssl_normalised in {"disable", "off", "false"}:
            connect_args["ssl"] = False
        elif ssl_normalised in {"require", "required", "verify-full", "verify-ca", "true"}:
            # ``True`` enforces SSL; asyncpg will validate certificates based on
            # the environment (Neon, Supabase, etc.).
            connect_args["ssl"] = True
        else:
            # For other modes (e.g. ``prefer``/``allow``) we omit the argument,
            # letting asyncpg pick the default behaviour.
            connect_args.pop("ssl", None)
    elif drivername.startswith("postgres"):
        # Other PostgreSQL drivers (e.g. psycopg) understand ``sslmode`` so we
        # restore the original value.
        query_params["sslmode"] = sslmode_value

if query_params != original_query_params:
    url_obj = url_obj.set(query=query_params)
    database_url = url_obj.render_as_string(hide_password=False)

if drivername.startswith("sqlite"):
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