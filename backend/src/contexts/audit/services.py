import json
import uuid
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.audit.models import AuditLog
from src.contexts.audit.repositories import AuditLogRepository


class AuditLogService:
    """Orchestrates security and action auditing across the platform."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = AuditLogRepository(db)

    async def log_action(
        self,
        tenant_id: str,
        action: str,
        resource_type: str,
        user_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Writes a structured security log record to PostgreSQL database."""
        details_str = json.dumps(details) if details else None

        audit_entity = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details_str,
        )
        return await self.repo.create(audit_entity)
