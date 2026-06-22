from redis.asyncio import Redis, ConnectionPool
from src.core.config import settings
from src.core.observability.logging import get_logger

logger = get_logger("src.infrastructure.redis.client")

# Global Redis connection pool instance
redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=50,
    decode_responses=True,
)


def get_redis_client() -> Redis:
    """Returns a client instance connected to the global pool."""
    return Redis(connection_pool=redis_pool)


async def check_redis_health() -> bool:
    """Verifies Redis connection liveness by executing a ping command."""
    client = get_redis_client()
    try:
        await client.ping()
        return True
    except Exception as exc:
        logger.error("Redis health check failed", error=str(exc))
        return False
    finally:
        await client.close()
