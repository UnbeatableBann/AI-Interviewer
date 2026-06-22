import time
import uuid
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from src.core.constants import PROCESS_TIME_HEADER, REQUEST_ID_HEADER
from src.core.observability.logging import get_logger
from src.shared.utils.context import get_tenant_id

logger = get_logger("src.api.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Correlation tracer and metric logger interceptor."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Generate correlation request tracking ID
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Bind correlation variables to contextvars so any logger output carries it
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        # Retrieve client IP and user agent safely
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request ingestion
        logger.info(
            "HTTP request started",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            user_agent=user_agent,
            tenant_id=get_tenant_id(),
        )

        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            # Inject correlation ID in downstream response headers
            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers[PROCESS_TIME_HEADER] = f"{process_time:.4f}s"

            # Record Prometheus request latency
            from src.core.observability import HTTP_REQUEST_LATENCY

            HTTP_REQUEST_LATENCY.labels(
                method=request.method,
                path=request.url.path,
                status_code=str(response.status_code),
            ).observe(process_time)

            logger.info(
                "HTTP request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(process_time, 4),
                tenant_id=get_tenant_id(),
            )
            return response
        except Exception as exc:
            process_time = time.perf_counter() - start_time

            # Record Prometheus request latency for failed request (500 Internal Server Error)
            from src.core.observability import HTTP_REQUEST_LATENCY

            HTTP_REQUEST_LATENCY.labels(
                method=request.method,
                path=request.url.path,
                status_code="500",
            ).observe(process_time)

            logger.error(
                "HTTP request failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                duration_seconds=round(process_time, 4),
                tenant_id=get_tenant_id(),
                exc_info=True,
            )
            raise exc
        finally:
            structlog.contextvars.clear_contextvars()
