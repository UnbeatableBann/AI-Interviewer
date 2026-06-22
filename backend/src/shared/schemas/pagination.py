from math import ceil
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field
from src.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class PageParams(BaseModel):
    """Query parameters validator for offset pagination."""

    page: int = Field(DEFAULT_PAGE, ge=1, description="Page index (1-based index).")
    size: int = Field(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="Number of records returned per page.",
    )

    @property
    def offset(self) -> int:
        """Returns computed offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedMeta(BaseModel):
    """Metadata detailing the bounds of a paginated query."""

    total_items: int = Field(
        ..., description="Grand total number of records matching criteria."
    )
    page: int = Field(..., description="Current page returned.")
    size: int = Field(..., description="Record limit per page.")
    total_pages: int = Field(..., description="Calculated total pages available.")
    has_next: bool = Field(
        ..., description="Flag showing if more records exist after this page."
    )
    has_prev: bool = Field(
        ..., description="Flag showing if records exist prior to this page."
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard generic wrapper payload model for list query pagination results."""

    items: List[T] = Field(
        ..., description="List of items corresponding to the requested page context."
    )
    meta: PaginatedMeta = Field(..., description="Dynamic bounds metadata parameters.")

    @classmethod
    def create(
        cls, items: List[T], total_items: int, params: PageParams
    ) -> "PaginatedResponse[T]":
        """Calculates parameters dynamically and initializes a paginated response wrapper."""
        total_pages = ceil(total_items / params.size) if total_items > 0 else 0
        return cls(
            items=items,
            meta=PaginatedMeta(
                total_items=total_items,
                page=params.page,
                size=params.size,
                total_pages=total_pages,
                has_next=params.page < total_pages,
                has_prev=params.page > 1,
            ),
        )
