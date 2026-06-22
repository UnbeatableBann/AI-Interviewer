from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from src.api.dependencies.db import get_db
from src.infrastructure.redis.client import check_redis_health
from src.infrastructure.qdrant.client import check_qdrant_health
from src.infrastructure.minio.client import check_minio_health
from src.shared.schemas.responses import APIResponse

router = APIRouter(prefix="/health", tags=["system-health"])


async def check_db_health(db: AsyncSession) -> bool:
    """Verifies relational database ping check is successful."""
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("", response_model=APIResponse[Dict[str, str]])
async def check_health(
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Dict[str, str]]:
    """Runs connectivity check routines for all backend subsystems."""
    db_ok = await check_db_health(db)
    redis_ok = await check_redis_health()
    qdrant_ok = await check_qdrant_health()
    minio_ok = await check_minio_health()

    status_map = {
        "api": "healthy",
        "database": "healthy" if db_ok else "unhealthy",
        "redis": "healthy" if redis_ok else "unhealthy",
        "qdrant": "healthy" if qdrant_ok else "unhealthy",
        "minio": "healthy" if minio_ok else "unhealthy",
    }

    # If any system is unhealthy, we mark the whole response success flag as False
    system_healthy = db_ok and redis_ok and qdrant_ok and minio_ok

    if not system_healthy:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail=APIResponse(
                success=False,
                data=status_map,
                error={
                    "code": "HEALTH_CHECK_FAILURE",
                    "message": "One or more infrastructure backends are unresponsive.",
                },
            ).model_dump(),
        )

    return APIResponse(
        success=True,
        data=status_map,
    )
