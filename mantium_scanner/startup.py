from mantium_scanner.db_utils import async_engine
from mantium_scanner.models.base import Base


async def create_tables() -> None:
    """Create database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def startup_event() -> None:
    """Run startup events"""
    await create_tables()
