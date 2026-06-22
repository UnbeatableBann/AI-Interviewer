from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from src.api.middleware.exceptions import register_exception_handlers
from src.api.middleware.hardening import (
    IdempotencyMiddleware,
    RateLimiterMiddleware,
    SecurityHeadersMiddleware,
)
from src.api.middleware.logging import LoggingMiddleware
from src.api.middleware.tenant import TenantMiddleware
from src.api.v1 import auth, candidates, evaluations, health, interviews, rag, tenants
from src.core.config import settings
from src.core.observability.logging import get_logger, setup_logging
from src.shared.schemas.responses import APIResponse

logger = get_logger("src.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handles startup and shutdown configurations for the API server."""
    # 1. Initialize structured logging configuration
    setup_logging()
    logger.info("Initializing Interviewer Intelligence Platform backend services...")

    # Initialize OpenTelemetry Tracing and instrument DB connection
    from src.core.database import engine
    from src.core.observability import setup_otel

    setup_otel(app, db_engine=engine)

    # 2. Attach standard sessionmaker to application state for middleware access
    from src.core.database import AsyncSessionLocal

    app.state.db_sessionmaker = AsyncSessionLocal

    yield

    logger.info("Tearing down platform backend services...")


# Initialize application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount Custom Production Middlewares (Executed in reverse order of addition)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(LoggingMiddleware)

# Register Custom Exception formatting
register_exception_handlers(app)

# Initialize and register routes
api_router = APIRouter(prefix=settings.API_V1_STR)

# Register routers
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(candidates.router)
api_router.include_router(interviews.router)
api_router.include_router(evaluations.router)
api_router.include_router(rag.router)


# Basic base root route for server checks
@app.get("/", tags=["root"])
async def root_redirect() -> APIResponse[dict[str, str]]:
    """Returns basic server information payload."""
    return APIResponse(
        success=True,
        data={
            "status": "online",
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )


@app.get("/metrics", tags=["observability"])
async def prometheus_metrics():
    """Exposes platform-level metrics for Prometheus scraping."""
    from fastapi import Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    """
    Return the Scalar API reference.

    This endpoint is hidden from OpenAPI/Swagger docs (`include_in_schema=False`).
    """
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar")


app.include_router(api_router)
