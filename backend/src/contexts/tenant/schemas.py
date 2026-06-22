from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TenantCreate(BaseModel):
    """Payload to provision a new tenant namespace."""

    id: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Slug URL identifier (lowercase, alphanumeric, hyphens).",
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Company/Organization business name.",
    )
    tier: str = Field(
        "STANDARD", description="Subscription tier: STANDARD, ENTERPRISE, DEDICATED."
    )

    @field_validator("id")
    @classmethod
    def validate_id_slug(cls, v: str) -> str:
        """Validates that slug contains only lowercase alphanumeric characters and hyphens."""
        import re

        if not re.match(r"^[a-z0-9\-]+$", v):
            raise ValueError(
                "Tenant ID must consist of lowercase alphanumeric letters and hyphens only."
            )
        return v


class TenantUpdate(BaseModel):
    """Payload to modify tenant profile details."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    tier: Optional[str] = Field(None)


class TenantResponse(BaseModel):
    """API payload serializer for Tenant operations."""

    id: str
    name: str
    tier: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
