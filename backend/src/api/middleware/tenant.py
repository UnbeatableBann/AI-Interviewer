import re
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from src.core.constants import TENANT_HEADER
from src.shared.utils.context import clear_context, set_tenant_id

# Public URL patterns that bypass strict tenant header validation
PUBLIC_URL_PATTERNS = [
    re.compile(r"^/$"),
    re.compile(r"^/docs"),
    re.compile(r"^/redoc"),
    re.compile(r"^/scalar"),
    re.compile(r"^/openapi.json"),
    re.compile(r"^/api/v1/auth/login"),
    re.compile(r"^/api/v1/auth/register"),
    re.compile(r"^/api/v1/health"),
    re.compile(r"^/metrics"),
]


class TenantMiddleware(BaseHTTPMiddleware):
    """Enforces tenant header extraction and request isolation bounds."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        clear_context()  # Always clear context to prevent leakage between threads

        tenant_id = request.headers.get(TENANT_HEADER)
        path = request.url.path

        # Determine if path is public and bypasses check
        is_public = any(pattern.match(path) for pattern in PUBLIC_URL_PATTERNS)

        if not tenant_id and not is_public:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "MISSING_TENANT_HEADER",
                        "message": f"The {TENANT_HEADER} header is required to complete this request.",
                        "details": None,
                    },
                },
            )

        if tenant_id:
            sessionmaker = getattr(request.app.state, "db_sessionmaker", None)
            if sessionmaker:
                from src.contexts.tenant.repositories import TenantRepository

                async with sessionmaker() as db:
                    repo = TenantRepository(db)
                    tenant = await repo.get_by_id(tenant_id)
                    if not tenant:
                        return JSONResponse(
                            status_code=404,
                            content={
                                "success": False,
                                "data": None,
                                "error": {
                                    "code": "TENANT_NOT_FOUND",
                                    "message": f"Tenant namespace '{tenant_id}' is not registered on this platform.",
                                    "details": None,
                                },
                            },
                        )
                    if tenant.status != "ACTIVE":
                        return JSONResponse(
                            status_code=403,
                            content={
                                "success": False,
                                "data": None,
                                "error": {
                                    "code": "TENANT_SUSPENDED",
                                    "message": f"Tenant namespace '{tenant_id}' has been suspended.",
                                    "details": None,
                                },
                            },
                        )
            set_tenant_id(tenant_id)

        try:
            response = await call_next(request)
            return response
        finally:
            clear_context()  # Ensure cleanup at end of request loop
