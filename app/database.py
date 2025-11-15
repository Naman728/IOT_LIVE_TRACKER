from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Base class for models
Base = declarative_base()

# Initialize engine and session factory as None (lazy initialization)
engine = None
AsyncSessionLocal = None


def init_db():
    """Initialize database engine and session factory."""
    global engine, AsyncSessionLocal
    
    if engine is None:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True,
            future=True
        )
        
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    return engine, AsyncSessionLocal


# Initialize on import (but handle errors gracefully)
try:
    init_db()
except Exception:
    # If initialization fails (e.g., missing dependencies), 
    # it will be retried when actually used
    pass


# Dependency for FastAPI
async def get_db():
    # Ensure database is initialized
    if AsyncSessionLocal is None:
        init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

