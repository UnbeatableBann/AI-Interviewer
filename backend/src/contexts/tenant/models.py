from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class Tenant(Base):
    """Core Tenant organization entity."""

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., "acme-corp"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[str] = mapped_column(
        String(20), default="STANDARD", nullable=False
    )  # STANDARD, ENTERPRISE, DEDICATED
    status: Mapped[str] = mapped_column(
        String(20), default="ACTIVE", nullable=False
    )  # ACTIVE, SUSPENDED

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
