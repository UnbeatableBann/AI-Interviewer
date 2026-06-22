from minio import Minio
from src.core.config import settings
from src.core.observability.logging import get_logger

logger = get_logger("src.infrastructure.minio.client")


def get_minio_client() -> Minio:
    """Instantiates and returns a Minio client connection."""
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


async def check_minio_health() -> bool:
    """Validates connectivity to MinIO by checking bucket status."""
    try:
        client = get_minio_client()
        # Verify if target bucket exists, creating it if missing
        if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
            client.make_bucket(settings.MINIO_BUCKET_NAME)
        return True
    except Exception as exc:
        logger.error("MinIO health check failed", error=str(exc))
        return False
