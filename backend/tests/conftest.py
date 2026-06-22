from typing import AsyncGenerator
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.main import app
from src.core.database import Base
from src.api.dependencies.db import get_db


from sqlalchemy.pool import StaticPool

# Test database connection configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
    poolclass=StaticPool,
)


TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def initialize_test_database() -> AsyncGenerator[None, None]:
    """Creates database schema before test runners start execution."""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields clean transaction-wrapped sessions for test isolation checks."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Returns an async HTTP client executing requests against application routers."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Override standard database dependency provider
    app.dependency_overrides[get_db] = override_get_db

    # Override middleware sessionmaker with test isolated SQLite context
    app.state.db_sessionmaker = TestingSessionLocal

    # Configure httpx AsyncClient using modern ASGITransport syntax
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
