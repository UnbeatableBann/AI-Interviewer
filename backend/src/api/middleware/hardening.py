import json
import time
from typing import Any, Awaitable, Callable, Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core.observability.logging import get_logger
from src.infrastructure.redis.client import get_redis_client
from src.shared.utils.context import get_tenant_id

logger = get_logger("src.api.middleware.hardening")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces critical security headers on all outgoing API payloads."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)

        # Inject standard security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Skip injecting strict Content-Security-Policy on documentation pages to allow external CDNs (Swagger/Scalar UI)
        path = request.url.path
        if path not in ["/docs", "/redoc", "/scalar", "/openapi.json"]:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; frame-ancestors 'none';"
            )
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )

        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Redis-backed rate limiter for IPs and tenants, failing open on database offline."""

    def __init__(
        self,
        app: Any,
        ip_limit: int = 100,  # Max requests per minute per IP
        tenant_limit: int = 500,  # Max requests per minute per Tenant
    ) -> None:
        super().__init__(app)
        self.ip_limit = ip_limit
        self.tenant_limit = tenant_limit

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Bypass rate limits for metrics/docs/redoc/health checks
        path = request.url.path
        if path in [
            "/metrics",
            "/docs",
            "/redoc",
            "/scalar",
            "/openapi.json",
            "/api/v1/health",
        ]:
            return await call_next(request)

        client = get_redis_client()
        current_minute = int(time.time() / 60)

        # 1. Enforce IP rate limits
        client_ip = request.client.host if request.client else "unknown"
        ip_key = f"ratelimit:ip:{client_ip}:{current_minute}"

        # 2. Enforce Tenant rate limits
        tenant_id = get_tenant_id() or request.headers.get("X-Tenant-ID")
        tenant_key = (
            f"ratelimit:tenant:{tenant_id}:{current_minute}" if tenant_id else None
        )

        try:
            # IP limit validation
            async with client.pipeline(transaction=True) as pipe:
                pipe.incr(ip_key)
                pipe.expire(ip_key, 120)
                res = await pipe.execute()
                ip_count = res[0]

            if ip_count > self.ip_limit:
                logger.warning("IP rate limit exceeded", ip=client_ip, count=ip_count)
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests from this IP. Please try again later.",
                            "details": {"limit": self.ip_limit},
                        },
                    },
                )

            # Tenant limit validation
            if tenant_key:
                async with client.pipeline(transaction=True) as pipe:
                    pipe.incr(tenant_key)
                    pipe.expire(tenant_key, 120)
                    res = await pipe.execute()
                    tenant_count = res[0]

                if tenant_count > self.tenant_limit:
                    logger.warning(
                        "Tenant rate limit exceeded",
                        tenant_id=tenant_id,
                        count=tenant_count,
                    )
                    return JSONResponse(
                        status_code=429,
                        content={
                            "success": False,
                            "data": None,
                            "error": {
                                "code": "TENANT_RATE_LIMIT_EXCEEDED",
                                "message": "Tenant API consumption limit exceeded.",
                                "details": {"limit": self.tenant_limit},
                            },
                        },
                    )

        except Exception as exc:
            # Fail open if Redis is offline so API stays available
            logger.error("Rate limiter Redis failure, passing through", error=str(exc))
        finally:
            await client.aclose()

        return await call_next(request)


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Enforces idempotent transaction bounds using an 'Idempotency-Key' header context."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Enforce check only on state-modifying requests
        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        tenant_id = get_tenant_id() or request.headers.get("X-Tenant-ID") or "global"
        redis_key = f"idempotency:{tenant_id}:{idempotency_key}"

        client = get_redis_client()
        try:
            # Check if key is already registered in Redis
            cached_val = await client.get(redis_key)
            if cached_val:
                if cached_val == "PROCESSING":
                    logger.warning(
                        "Parallel request detected for idempotency key",
                        key=idempotency_key,
                    )
                    return JSONResponse(
                        status_code=409,
                        content={
                            "success": False,
                            "data": None,
                            "error": {
                                "code": "IDEMPOTENCY_CONFLICT",
                                "message": "A duplicate request with this key is already in progress.",
                                "details": None,
                            },
                        },
                    )

                # Re-serve cached response
                try:
                    cached_resp: Dict[str, Any] = json.loads(cached_val)
                    logger.info(
                        "Serving cached idempotent response", key=idempotency_key
                    )

                    # Filter/reconstruct headers safely
                    headers = dict(cached_resp.get("headers", []))
                    headers["X-Cache-Lookup"] = "HIT (Idempotent)"

                    return Response(
                        content=cached_resp["body"].encode("utf-8"),
                        status_code=cached_resp["status_code"],
                        headers=headers,
                    )
                except Exception as e:
                    logger.error(
                        "Failed to parse cached idempotent payload", error=str(e)
                    )

            # Register processing lock in Redis (5-minute safety window)
            await client.setex(redis_key, 300, "PROCESSING")

        except Exception as exc:
            logger.error(
                "Idempotency lock check failed, processing request", error=str(exc)
            )
        finally:
            await client.aclose()

        # Execute request downstream
        response_body = b""
        try:
            response = await call_next(request)

            # Cache the response only on successful/stable statuses
            if 200 <= response.status_code < 400:
                # Read response body stream (consuming it)
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Reconstruct Response
                new_response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

                try:
                    client = get_redis_client()
                    cache_payload = {
                        "status_code": response.status_code,
                        "headers": list(response.headers.items()),
                        "body": response_body.decode("utf-8", errors="replace"),
                    }
                    # Keep idempotent cache records for 24 hours
                    await client.setex(redis_key, 86400, json.dumps(cache_payload))
                except Exception as e:
                    logger.error(
                        "Failed writing idempotent result to cache", error=str(e)
                    )
                finally:
                    await client.aclose()

                return new_response
            else:
                # Clear processing lock on error response so client can retry immediately
                try:
                    client = get_redis_client()
                    await client.delete(redis_key)
                except Exception as e:
                    logger.error(
                        "Failed clearing idempotency processing lock", error=str(e)
                    )
                finally:
                    await client.aclose()
                return response

        except Exception as exc:
            # Clear lock on critical application error
            try:
                client = get_redis_client()
                await client.delete(redis_key)
            except Exception as e:
                logger.error(
                    "Failed clearing idempotency lock on exception", error=str(e)
                )
            finally:
                await client.aclose()
            raise exc
