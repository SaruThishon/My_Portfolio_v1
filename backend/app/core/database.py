from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Vercel serverless: use NullPool (no persistent connections between invocations).
# Local dev / traditional server: use connection pool for performance.
_pool_kwargs = (
    {"poolclass": NullPool}
    if settings.ENVIRONMENT == "production"
    else {"pool_size": 10, "max_overflow": 20, "pool_pre_ping": True}
)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    # Supabase transaction pooler (port 6543) uses pgbouncer which does not
    # support prepared statements. Setting cache size to 0 disables them.
    connect_args={"statement_cache_size": 0},
    **_pool_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
