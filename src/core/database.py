from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings

# Create highly-concurrent async connection engine
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,      #  validates connections before issuing queries
    echo=False,              # Set to True for raw SQL generation logs during debugging
    pool_size=20,            
    max_overflow=10          
)

# Operational Session factory bound to the async engine
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents lazy-loading issues after transaction closure
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    """Abstract mapping base for SQLAlchemy 2.0 Declarative Models."""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency yield-generator providing transaction-scoped DB contexts."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
