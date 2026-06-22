from qdrant_client import AsyncQdrantClient
from src.core.config import settings
from src.core.observability.logging import get_logger

logger = get_logger("src.infrastructure.qdrant.client")


def get_qdrant_client() -> AsyncQdrantClient:
    """Initializes and returns an AsyncQdrantClient instance."""
    return AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY,
    )


async def check_qdrant_health() -> bool:
    """Checks the health of the Qdrant server."""
    client = get_qdrant_client()
    try:
        # Simple retrieval of server info to verify connectivity
        await client.get_collections()
        return True
    except Exception as exc:
        logger.error("Qdrant health check failed", error=str(exc))
        return False
    finally:
        await client.close()
