from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # Make sure you have these imports
from sqlalchemy.orm import Session, scoped_session, sessionmaker

DATABASE_URL = 'sqlite:///./test.db'  # Revert DATABASE_URL to use "sqlite"
sync_engine = create_engine(DATABASE_URL, echo=True)  # Create a synchronous engine

DATABASE_ASYNC_URL = 'sqlite+aiosqlite:///./test.db'  # Add a new URL for async engine
async_engine = create_async_engine(DATABASE_ASYNC_URL, echo=True)  # Create an async engine

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=sync_engine))


# Update the get_async_db function to use the async_engine
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session"""
    async with AsyncSession(async_engine, expire_on_commit=False) as session:  # Use async_engine here
        yield session


def get_db() -> Generator[Session, None, None]:
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ['get_db', 'get_async_db', 'async_engine']
