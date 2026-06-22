from typing import Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from src.core.exceptions import IIPException
from src.core.observability.logging import get_logger
from src.shared.schemas.responses import APIResponse, ErrorDetail

logger = get_logger("src.api.middleware.exceptions")


def _clean_error(value: Any) -> Any:
    """Recursively converts non-serializable objects like Exceptions or Types to strings."""
    if isinstance(value, dict):
        return {k: _clean_error(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_clean_error(v) for v in value]
    elif isinstance(value, Exception):
        return str(value)
    elif isinstance(value, type):
        return value.__name__
    return value


def register_exception_handlers(app: FastAPI) -> None:
    """Attaches unified JSON error format mapping handlers to the FastAPI app instance."""

    @app.exception_handler(IIPException)
    async def iip_exception_handler(
        request: Request, exc: IIPException
    ) -> JSONResponse:
        logger.warn(
            "Domain exception caught",
            code=exc.code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                APIResponse(
                    success=False,
                    data=None,
                    error=ErrorDetail(code=exc.code, message=exc.message),
                )
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        logger.warn("Request validation failed", path=request.url.path, errors=errors)
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                APIResponse(
                    success=False,
                    data=None,
                    error=ErrorDetail(
                        code="VALIDATION_ERROR",
                        message="Request payload validation failed.",
                        details=_clean_error(errors),
                    ),
                )
            ),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        logger.error(
            "Pydantic schema validation failed", path=request.url.path, errors=errors
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                APIResponse(
                    success=False,
                    data=None,
                    error=ErrorDetail(
                        code="INTERNAL_VALIDATION_ERROR",
                        message="Internal data structure validation failed.",
                        details=_clean_error(errors),
                    ),
                )
            ),
        )

    @app.exception_handler(IntegrityError)
    async def db_integrity_exception_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        logger.error(
            "Database integrity violation error",
            path=request.url.path,
            details=str(exc),
        )
        return JSONResponse(
            status_code=409,
            content=jsonable_encoder(
                APIResponse(
                    success=False,
                    data=None,
                    error=ErrorDetail(
                        code="DATABASE_CONFLICT",
                        message="A data conflict occurred while writing resource to database.",
                    ),
                )
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled system exception occurred",
            path=request.url.path,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                APIResponse(
                    success=False,
                    data=None,
                    error=ErrorDetail(
                        code="INTERNAL_SERVER_ERROR",
                        message="An unexpected system error occurred. Please contact administrator.",
                    ),
                )
            ),
        )
