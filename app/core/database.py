from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import make_url
from app.core.config import settings
import asyncio
import threading


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

# Flag and lock for lazy initialization (for serverless environments)
_models_initialized = False
_init_lock_storage = {}  # Store locks per event loop
_thread_lock = threading.Lock()  # Thread-safe lock to guard async lock creation


class Base(DeclarativeBase):
    pass


def get_json_type():
    db_url = settings.DATABASE_URL.lower()
    if "postgresql" in db_url or "postgres" in db_url:
        return JSONB
    else:
        return JSON


# Export for use in models
JSONType = get_json_type()


async def init_models():
    """Initialize database models by creating all tables."""
    global _models_initialized
    # Import models here to avoid circular imports
    from app.models import all_models  # noqa
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Simple connectivity check
    async with AsyncSessionLocal() as s:
        await s.execute(text("SELECT 1"))
    _models_initialized = True


def _get_init_lock():
    """Get or create an asyncio lock for the current event loop."""
    loop = asyncio.get_running_loop()
    loop_id = id(loop)
    
    # Use thread lock to safely access the storage
    with _thread_lock:
        if loop_id not in _init_lock_storage:
            _init_lock_storage[loop_id] = asyncio.Lock()
        return _init_lock_storage[loop_id]


async def ensure_models_initialized():
    """Ensure models are initialized (lazy initialization for serverless)."""
    global _models_initialized
    if _models_initialized:
        return
    
    # Get lock for current event loop
    init_lock = _get_init_lock()
    async with init_lock:
        # Check again after acquiring lock (double-check pattern)
        if _models_initialized:
            return
        try:
            await init_models()
            print("✅ Database tables initialized (lazy init).")
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}")
            # Don't raise - allow retry on next request


async def get_session() -> AsyncSession:
    """Get database session, ensuring tables are initialized first."""
    await ensure_models_initialized()
    async with AsyncSessionLocal() as session:
        yield session