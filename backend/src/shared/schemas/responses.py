from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

# Define TypeVar for generic payload typing
T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Detailed error object returned within standard error responses."""

    code: str = Field(..., description="Application-specific string error code.")
    message: str = Field(..., description="Human-readable description of error.")
    details: Optional[Any] = Field(
        None,
        description="Optional extra metadata, stack parameters, or validation details.",
    )


class APIResponse(BaseModel, Generic[T]):
    """Standard generic wrapper payload model for all REST API responses."""

    success: bool = Field(
        ..., description="Flag indicating if the operation succeeded."
    )
    data: Optional[T] = Field(
        None, description="Response payload containing typed data results."
    )
    error: Optional[ErrorDetail] = Field(
        None, description="Detailed error information, if success is False."
    )
    meta: Optional[dict[str, Any]] = Field(
        None, description="Optional pagination/filtering/tracing metadata."
    )
