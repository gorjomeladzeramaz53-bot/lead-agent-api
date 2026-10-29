from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings

settings = get_settings()

# Configure specific connection arguments for SQLite if applicable
connect_args = {"check_same_thread": False} if "sqlite" in str(settings.DATABASE_URL) else {}

# Initialize the SQLAlchemy async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,
    connect_args=connect_args,
)

# Configure the async session maker factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an asynchronous database session.
    Handles automatic commit on success and rollback on exceptions,
    ensuring proper resource cleanup in the finally block.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()