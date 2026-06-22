from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db as _get_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper to yield active async db sessions."""
    async for session in _get_db():
        yield session
